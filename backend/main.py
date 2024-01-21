from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated, Union
from datetime import datetime, timedelta, timezone
import json
import os
from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import Session, Mapped, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
import pymssql
from pymemcache.client import base
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from models import User, Role
from schemas import UserSchema

# import models
from database import engine, SessionLocal, Base

load_dotenv()

Base.metadata.create_all(bind=engine)


mc = base.Client((os.getenv("MC_SERVER"), 11211))


SECRET_KEY = os.getenv("SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "id": 1,
        "username": "johndoe",
        "email": "johndoe@example.com",
        "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
        "roles": [{"roleName": "user"}, {"roleName": "other"}],
    },
    "alice": {
        "id": 2,
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "password": "fakehashedsecret2",
        "disabled": True,
        "roles": [{"roleName": "user"}, {"roleName": "other"}],
    },
}

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str, db: Session):
    user = db.execute(select(User.User).where(User.User.username == username)).first()[
        0
    ]

    if user:
        user_dict = UserSchema.UserInDB(
            user_id=user.user_id,
            username=user.username,
            password=user.password,
            email=user.email,
            disabled=user.disabled,
            role_id=user.role_id,
        )
        return UserSchema.UserInDB(**user_dict.model_dump())


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[UserSchema.User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: Annotated[UserSchema.User, Depends(get_current_active_user)]
):
    if "admin" not in [role.roleName for role in current_user.roles]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )
    return current_user


async def get_current_normal_user(
    current_user: Annotated[UserSchema.User, Depends(get_current_active_user)]
):
    if "user" not in [role.roleName for role in current_user.roles]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )
    return current_user


async def get_current_other_user(
    current_user: Annotated[UserSchema.User, Depends(get_current_active_user)]
):
    if "other" not in [role.roleName for role in current_user.roles]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )
    return current_user


def authenticate_user(username: str, password: str, db: Session):
    user = get_user(username, db)

    if not user:
        return False

    if not verify_password(password, user.password):
        return False

    return user


def load_dbs(refresh: bool = False):
    # Check if the result is already cached
    result = mc.get("database_list")
    if result is not None and not refresh:
        return
    with Session(autocommit=False, autoflush=False, bind=engine) as db:
        query = text("SELECT name FROM sys.databases")
        results = db.execute(query).fetchall()
        databases = [result[0] for result in results]
        json_dbs = json.dumps(databases, default=str)
        # Cache the result
        mc.set("database_list", json_dbs)


load_dbs()


def get_dbs():
    dbs = mc.get("database_list")
    # convert statuses to dict
    dbs = json.loads(dbs)
    return dbs


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.post("/signup")
async def signup(userSignup: UserSchema.UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    existing_user = db.execute(
        select(User.User).where(
            (User.User.username == userSignup.username)
            | (User.User.email == userSignup.email)
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    user = User.User(
        **userSignup.model_dump(exclude=["role_id"]),
        role_id=db.execute(
            select(Role.Role).where(Role.Role.role_id == userSignup.role_id)
        )
        .first()[0]
        .role_id,
    )
    user.password = get_password_hash(user.password)

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "User created successfully"}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        )


@app.get("/users/me")
async def read_users_me(
    current_active_user: Annotated[UserSchema.User, Depends(get_current_active_user)]
):
    return current_active_user


@app.get("/")
async def hello_world(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"message": "Hello World"}


@app.get("/sms-list")
async def get_all_sms():
    return {"message": "All the SMS"}


@app.get("/get_all_databases_cached")
async def get_all_databases_chached():
    return get_dbs()


@app.get("/get_all_databases")
async def get_all_databases(db: Session = Depends(get_db)):
    query = text("SELECT name FROM sys.databases")
    results = db.execute(query).fetchall()
    databases = [result[0] for result in results]
    return databases


@app.get("/phone/{mobile_number}")
async def get_messages(mobile_number: str, db: Session = Depends(get_db)):
    try:
        messages = []

        try:
            query = text(
                """
                DECLARE @command varchar(MAX)
                CREATE TABLE #TempResults (
                    ToAddress varchar(MAX),
                    Body varchar(MAX),
                    StatusID int
                )

                SELECT @command = 'IF ''?'' LIKE ''au%'' OR ''?'' LIKE ''ar%'' 
                BEGIN 
                    USE ? 
                    DECLARE @table_name varchar(MAX)
                    
                    IF (LOWER(LEFT(''?'', 2)) = ''ar'')
                        SET @table_name = ''ArchMessages''
                    ELSE
                        SET @table_name = ''Messages''

                    IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = @table_name AND COLUMN_NAME = ''OriginalID'')
                        BEGIN
                            DECLARE @sql_query1 NVARCHAR(MAX)
                            SELECT @sql_query1 = ''INSERT INTO #TempResults (ToAddress, Body, StatusID) '' +
                                ''select ToAddress, Body, StatusID '' +
                                ''from '' + @table_name + '' a, '' + @table_name + ''_Sms'' + '' b '' +
                                ''where a.OriginalID=b.MessageID AND ToAddress = """
                + mobile_number
                + """ ''
                            EXEC sp_executesql @sql_query1
                        END
                    ELSE
                        BEGIN
                            DECLARE @sql_query2 NVARCHAR(MAX)
                            SELECT @sql_query2 = ''INSERT INTO #TempResults (ToAddress, Body, StatusID) '' +
                                ''select ToAddress, Body, StatusID '' +
                                ''from '' + @table_name + '' a, '' + @table_name + ''_Sms'' + '' b '' +
                                ''where a.id=b.MessageID AND ToAddress = """
                + mobile_number
                + """ ''
                            EXEC sp_executesql @sql_query2
                        END
                END'

                EXEC sp_MSforeachdb @command
 
                SELECT * FROM #TempResults

                DROP TABLE #TempResults
                """
            )
            results = db.execute(query).fetchall()
            cureent_msg = [
                {
                    "ToAddress": result[0],
                    # "senttime": result[1],
                    "Body": result[1],
                    "StatusID": result[2],
                }
                for result in results
            ]
            if cureent_msg is not None:
                messages = messages + cureent_msg
        except Exception as e:
            print(e)
            # query = text(
            #     f"select ToAddress,senttime, Body,StatusID  from [{all_dbs[i]}].dbo.{table_name} a,[{all_dbs[i]}].dbo.{table_name}_Sms b where a.id=b.MessageID and  ToAddress like :mobile_number order by SentTime desc"
            # )
            # results = db.execute(
            #     query, {"mobile_number": f"%{mobile_number}%"}
            # ).fetchall()
            # cureent_msg = [
            #     {
            #         "ToAddress": result[0],
            #         "senttime": result[1],
            #         "Body": result[2],
            #         "StatusID": result[3],
            #     }
            #     for result in results
            # ]
            # if cureent_msg is not None:
            #     messages = messages + cureent_msg
            # print(all_dbs[i])
            # pass

        return messages
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error executing SQL query: {str(e)}"
        )


# select ToAddress, Body, StatusID
# from @dbname.dbo.@table_name a, @dbname.dbo.@table_name_Sms b
# where a.id=b.MessageID and  ToAddress like :mobile_number;

# DECLARE @dbname varchar(MAX) = '';
# DECLARE @table_name varchar(MAX) = '';
# DECLARE @rn INT = 1;

# WHILE @dbname IS NOT NULL
# BEGIN
#     SET @dbname = (SELECT name FROM (SELECT name, ROW_NUMBER() OVER (ORDER BY name) rn
#         FROM sys.databases WHERE ((name LIKE 'au%' OR name LIKE 'ar%') AND name <> 'auintegration')) t WHERE rn = @rn);

#     IF @dbname <> '' AND @dbname IS NOT NULL
#         BEGIN
#             IF (LOWER(LEFT(@dbname, 2)) = 'ar')
#                 SET @table_name = 'ArchMessages'
#             ELSE
#                 SET @table_name = 'Messages'

#             DECLARE @SQL NVARCHAR(MAX);
#             SET @SQL = N'USE ' + QUOTENAME(@dbname);
#             PRINT(@SQL);
#             EXECUTE(@SQL);

#             IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = QUOTENAME(@table_name) AND COLUMN_NAME = 'OriginalID')
#                 BEGIN
#                     DECLARE @sql_query1 NVARCHAR(MAX);
#                     SELECT @sql_query1 = 'select ToAddress, Body, StatusID ' +
#                         'from ' + QUOTENAME(@dbname) + '.dbo.' + QUOTENAME(@table_name) + ' a, ' + QUOTENAME(@dbname) + '.dbo.' + QUOTENAME(@table_name + '_Sms') + ' b ' +
#                         'where a.OriginalID=b.MessageID and  ToAddress like 123456789'
#                     EXEC sp_executesql @sql_query1;
#                 END
#             ELSE
#                 BEGIN
#                     DECLARE @sql_query2 NVARCHAR(MAX);
#                     SELECT @sql_query2 = 'select ToAddress, Body, StatusID ' +
#                         'from ' + QUOTENAME(@dbname) + '.dbo.' + QUOTENAME(@table_name) + ' a, ' + QUOTENAME(@dbname) + '.dbo.' + QUOTENAME(@table_name + '_Sms') + ' b ' +
#                         'where a.OriginalID=b.MessageID and  ToAddress like 123456789'
#                     EXEC sp_executesql @sql_query2;
#                 END
#         END
#     SET @rn = @rn + 1;
# END;
