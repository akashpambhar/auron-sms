from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os
from ldap3 import Server, Connection, ALL, SUBTREE
from typing import Annotated, Union
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from schemas import UserSchema, TokenSchema
from database import SessionLocal

router = APIRouter(prefix="/auth/ad", tags=["auth/ldap"])

SECRET_KEY = os.getenv("SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# SERVER
LDAP_HOST = os.getenv("LDAP_HOST")
LDAP_PORT = os.getenv("LDAP_PORT")
LDAP_DOMAIN = os.getenv("LDAP_DOMAIN")
LDAP_USE_SSL = os.getenv("LDAP_USE_SSL")
LDAP_START_TLS = os.getenv("LDAP_START_TLS")
LDAP_SSL_SKIP_VERIFY = os.getenv("LDAP_SSL_SKIP_VERIFY")
LDAP_BIND_DN = os.getenv("LDAP_BIND_DN")
LDAP_BIND_PASSWORD = os.getenv("LDAP_BIND_PASSWORD")
LDAP_SEARCH_FILTER = os.getenv("LDAP_SEARCH_FILTER")
LDAP_SEARCH_BASE_DNS = os.getenv("LDAP_SEARCH_BASE_DNS")

# SERVER GROUP MAPPINGS
LDAP_ADMINS_GROUP = os.getenv("LDAP_ADMINS_GROUP")
LDAP_USERS_GROUP = os.getenv("LDAP_USERS_GROUP")
LDAP_OTHERS_GROUP = os.getenv("LDAP_OTHERS_GROUP")


ad_oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="/auth/ad/signin", scheme_name="ad_oauth2_schema"
)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user(username: str):
    user = UserSchema.UserInDB(
        user_id=-1, username="", email="", role_id=-1, password=""
    )

    try:
        server = Server(LDAP_HOST, get_info=ALL)
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

    return UserSchema.UserInDB(**user.model_dump())


def get_current_user(token: Annotated[str, Depends(ad_oauth2_schema)]):
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
        token_data = TokenSchema.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


def get_current_admin_user(
    current_user: Annotated[UserSchema.User, Depends(get_current_user)]
):
    if 1 != current_user.role_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )
    return current_user


def get_current_normal_user(
    current_user: Annotated[UserSchema.User, Depends(get_current_user)]
):
    if 2 != current_user.role_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )
    return current_user


def get_current_other_user(
    current_user: Annotated[UserSchema.User, Depends(get_current_user)]
):
    if 3 != current_user.role_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )
    return current_user


def get_current_admin_and_normal_user(
    current_user: Annotated[UserSchema.User, Depends(get_current_user)]
):
    if current_user.role_id not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this resource",
        )
    return current_user


def authenticate_user(username, password):
    user = UserSchema.UserInDB(
        user_id=-1, username="", email="", role_id=-1, password=""
    )

    try:
        server = Server(LDAP_HOST, get_info=ALL)

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
    return UserSchema.UserInDB(**user.model_dump())


@router.post("/signin")
def login_for_access_token(
    user_signin: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> TokenSchema.Token:
    user = authenticate_user(user_signin.username, user_signin.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role_id},
        expires_delta=access_token_expires,
    )
    return TokenSchema.Token(access_token=access_token, token_type="bearer")


@router.get("/me")
def read_users_me(
    current_active_user: Annotated[UserSchema.User, Depends(get_current_user)]
):
    return current_active_user
