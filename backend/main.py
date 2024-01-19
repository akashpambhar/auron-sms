from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated, Union
from datetime import datetime, timedelta, timezone
import json
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
import pymssql
from pymemcache.client import base
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt

load_dotenv()

mc = base.Client((os.getenv("MC_SERVER"), 11211))

SQL_DB = os.getenv("SQL_DB")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_SERVER = os.getenv("SQL_SERVER")

SECRET_KEY = os.getenv("SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "id": 1,
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "alice": {
        "id": 2,
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "password": "fakehashedsecret2",
        "disabled": True,
    },
}

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    password: str


def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
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
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
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


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@app.get("/")
async def hello_world(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"message": "Hello World"}


connection_string = f"mssql+pymssql://{SQL_USER}:{SQL_PASSWORD}@{SQL_SERVER}/{SQL_DB}"
engine = create_engine(
    connection_string,
    creator=lambda: pymssql.connect(SQL_SERVER, SQL_USER, SQL_PASSWORD, SQL_DB),
)


def get_db():
    db = Session(autocommit=False, autoflush=False, bind=engine)
    try:
        yield db
    finally:
        db.close()


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
