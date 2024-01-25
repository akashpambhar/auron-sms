from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated, Union
from datetime import datetime, timedelta, timezone
import os
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from jose import JWTError, jwt
from models import User, Role
from schemas import UserSchema, TokenSchema
from database import SessionLocal

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_auth_scheme():
    return OAuth2PasswordBearer(tokenUrl="/auth")


oauth2_scheme = get_auth_scheme()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signin")
async def login_for_access_token(
    user_signin: UserSchema.UserSignIn,
    db: Annotated[Session, Depends(get_db)],
) -> TokenSchema.Token:
    user = authenticate_user(user_signin.username, user_signin.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role_id}, expires_delta=access_token_expires
    )
    return TokenSchema.Token(access_token=access_token, token_type="bearer")


@router.post("/signup")
async def signup(userSignup: UserSchema.UserSignUp, db: Session = Depends(get_db)):
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

    user = User.User(**userSignup.model_dump())
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
        token_data = TokenSchema.TokenData(username=username)
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


@router.get("/me")
async def read_users_me(
    current_active_user: Annotated[UserSchema.User, Depends(get_current_active_user)]
):
    return current_active_user
