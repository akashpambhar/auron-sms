from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated, Union
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from jose import jwt
from models import User
from schemas import UserSchema, TokenSchema
from database import get_db
from ldap3 import Server, Connection, ALL, SUBTREE
from utils.Utils import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ENUM_DATABASE,
    ENUM_ACTIVE_DIRECTORY,
    LDAP_HOST,
    LDAP_PORT,
    LDAP_DOMAIN,
    LDAP_BIND_DN,
    LDAP_BIND_PASSWORD,
    LDAP_SEARCH_FILTER,
    LDAP_SEARCH_BASE_DNS,
    LDAP_ADMINS_GROUP,
    LDAP_USERS_GROUP,
    LDAP_OTHERS_GROUP,
    credentials_exception,
    decode_jwt,
    insert_audit_trail
)

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/signin")
def login_for_access_token_using_database(
    request: Request,
    user_signin: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> TokenSchema.Token:
    user = authenticate_db_user(user_signin.username, user_signin.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role_id,
            "auth_mode": ENUM_DATABASE,
        },
        expires_delta=access_token_expires,
    )
    
    insert_audit_trail(request.client.host, request.url.path, request.method, request.query_params.__str__(), user.username, ENUM_DATABASE)

    return TokenSchema.Token(access_token=access_token, token_type="bearer")


@router.post("/ad/signin")
def login_for_access_token_using_ad(
    request: Request,
    user_signin: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
) -> TokenSchema.Token:
    user = authenticate_ad_user(user_signin.username, user_signin.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    existing_user = db.execute(
        select(User.User).where(
            (User.User.username == user_signin.username)
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    new_user = User.User(**user_signin.model_dump())
    new_user.password = get_password_hash(user.password)
    new_user.email = user_signin.username + "@" + LDAP_DOMAIN
    new_user.role_id = user.role_id

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print("User created successfully")
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role_id,
            "auth_mode": ENUM_ACTIVE_DIRECTORY,
        },
        expires_delta=access_token_expires,
    )

    insert_audit_trail(request.client.host, request.url.path, request.method, request.query_params.__str__(), user.username, ENUM_ACTIVE_DIRECTORY)

    return TokenSchema.Token(access_token=access_token, token_type="bearer")


@router.post("/signup")
def signup(
    request: Request,
    user_signup: UserSchema.UserSignUp,
    db: Session = Depends(get_db)
):
    existing_user = db.execute(
        select(User.User).where(
            (User.User.username == user_signup.username)
            | (User.User.email == user_signup.email)
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    user = User.User(**user_signup.model_dump())
    user.password = get_password_hash(user.password)

    try:
        db.add(user)
        db.commit()
        insert_audit_trail(request.client.host, request.url.path, request.method, request.query_params.__str__(), user.username, ENUM_DATABASE)
        return {"message": "User created successfully"}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        )


def verify_password(plain_password, password):
    return pwd_context.verify(plain_password, password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_db_user(username: str, db: Session):
    user = db.execute(select(User.User).where(User.User.username == username)).first()[
        0
    ]

    if user:
        return UserSchema.UserInDB(
            user_id=user.user_id,
            username=user.username,
            password=user.password,
            email=user.email,
            disabled=user.disabled,
            role_id=user.role_id,
        )


def get_ad_user(username: str):
    user = UserSchema.UserInDB(
        user_id=-1, username="", email="", role_id=-1, password=""
    )

    try:
        server = Server(LDAP_HOST, int(LDAP_PORT), get_info=ALL)
        conn = Connection(
            server, user=LDAP_BIND_DN, password=LDAP_BIND_PASSWORD, auto_bind=True
        )

        search_filter = LDAP_SEARCH_FILTER.replace("%s", username)
        conn.search(
            search_base=LDAP_SEARCH_BASE_DNS,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=["memberOf"],
        )

        if conn.entries:
            user.username = username
            roles = [str(role) for role in conn.entries[0].memberOf]

            print("User roles:", roles)

            if LDAP_ADMINS_GROUP in roles:
                user.role_id = 1
            elif LDAP_USERS_GROUP in roles:
                user.role_id = 2
            elif LDAP_OTHERS_GROUP in roles:
                user.role_id = 3
            else:
                print("Role not found for ", username)
                return None
        else:
            print("User not found.")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        conn.unbind()

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


def get_current_user(
    req: Request,
    db: Annotated[Session, Depends(get_db)],
):
    token = req.headers["authorization"].split(" ")[1]

    username, auth_mode = decode_jwt(token)

    if auth_mode == ENUM_DATABASE:
        user = get_db_user(username, db)
    elif auth_mode == ENUM_ACTIVE_DIRECTORY:
        user = get_ad_user(username)

    if user is None:
        raise credentials_exception
    return (user, auth_mode)


def get_current_active_user(
    current_user: Annotated[tuple, Depends(get_current_user)]
):
    if current_user[1] == ENUM_DATABASE and (current_user[0].disabled == None or current_user[0].disabled == True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user[0]


def get_current_admin_user(
    current_user: Annotated[UserSchema.User, Depends(get_current_active_user)]
):
    if (
        1 != current_user.role_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )
    return current_user


def get_current_normal_user(
    current_user: Annotated[UserSchema.User, Depends(get_current_active_user)]
):
    if (
        2 != current_user.role_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )
    return current_user


def get_current_other_user(
    current_user: Annotated[UserSchema.User, Depends(get_current_active_user)]
):
    if (
        3 != current_user.role_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )
    return current_user


def get_current_admin_and_normal_user(
    current_user: Annotated[UserSchema.User, Depends(get_current_active_user)]
):
    if (
        current_user.role_id not in [1, 2]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )
    return current_user


def authenticate_db_user(username: str, password: str, db: Session):
    user = get_db_user(username, db)

    if not user:
        return False

    if not verify_password(password, user.password):
        return False

    if user.disabled == True or user.disabled is None:
        return False

    return user


def authenticate_ad_user(username, password):
    user = UserSchema.UserInDB(
        user_id=-1, username="", email="", role_id=-1, password=""
    )

    try:
        server = Server(LDAP_HOST, int(LDAP_PORT), get_info=ALL)

        user_conn = Connection(
            server, user=f"{username}@{LDAP_DOMAIN}", password=password, auto_bind=True
        )

        user_conn.bind()

        if user_conn.result["result"] == 0:
            print("Authentication successful")
            user.username = username

            conn = Connection(
                server, user=LDAP_BIND_DN, password=LDAP_BIND_PASSWORD, auto_bind=True
            )

            search_filter = LDAP_SEARCH_FILTER.replace("%s", username)
            conn.search(
                search_base=LDAP_SEARCH_BASE_DNS,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=["memberOf"],
            )

            if conn.entries:
                roles = [str(role) for role in conn.entries[0].memberOf]

                print("User roles:", roles)

                if LDAP_ADMINS_GROUP in roles:
                    user.role_id = 1
                elif LDAP_USERS_GROUP in roles:
                    user.role_id = 2
                elif LDAP_OTHERS_GROUP in roles:
                    user.role_id = 3
                else:
                    print("Role not found for ", username)
                    return None
            else:
                print("User not found.")
                return None
        else:
            print("Authentication failed")
            return None

    except:
        print("Authentication failed")
        return None
    finally:
        try:
            user_conn.unbind()
            conn.unbind()
        except:
            """"""
    return user
