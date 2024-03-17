from fastapi import Depends, APIRouter, HTTPException, status, BackgroundTasks
from database import get_db
from typing import Annotated
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from schemas import UserSchema, ForgotPasswordSchema
from models import User, Role, PasswordToken
from routers import auth
from sqlalchemy import select, join, text, delete
import smtplib
from email.message import EmailMessage
import os
import secrets
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/users", tags=["users"])

MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
UI_URL = os.getenv("UI_URL")


def get_password_hash(password):
    return pwd_context.hash(password)


@router.get("")
def get_users(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_user)],
    db: Annotated[Session, Depends(get_db)],
):
    join_condition = User.User.role_id == Role.Role.role_id
    query = (
        select(User.User)
        .select_from(join(User.User, Role.Role, join_condition))
        .where(User.User.username != current_user.username and User.User.role_id != 1)
    )

    results = db.execute(query).fetchall()

    users = [
        {
            "user_id": result[0].user_id,
            "username": result[0].username,
            "email": result[0].email,
            "disabled": result[0].disabled,
            "role_id": result[0].role.role_id,
            "role_name": result[0].role.role_name,
        }
        for result in results
    ]

    return users


@router.get("/{user_id}")
def get_user_by_user_id(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_user)],
    user_id: str,
    db: Annotated[Session, Depends(get_db)],
):
    existing_user = db.execute(
        select(User.User).where(User.User.user_id == user_id)
    ).first()

    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    return existing_user[0]


@router.get("/search/{username}")
def get_user_by_user_username(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_user)],
    username: str,
    db: Annotated[Session, Depends(get_db)],
):
    native_sql_query = text(
        f"""
        SELECT * 
        FROM [user]
        JOIN role ON [user].role_id = role.role_id
        WHERE [user].username LIKE '%"""
        + username
        + """%\'"""
        + f"""
        AND [user].username != :username
        AND [user].role_id != 1 
        """
    )

    results = db.execute(native_sql_query, {"username": username}).fetchall()

    users = []

    if results:
        users = [
            {
                "user_id": result[0],
                "username": result[1],
                "email": result[3],
                "disabled": result[4],
                "role_id": result[5],
                "role_name": result[7],
            }
            for result in results
        ]

    return users


@router.post("")
def add_user(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_user)],
    user_create: UserSchema.UserCreate,
    db: Annotated[Session, Depends(get_db)],
):
    existing_user = db.execute(
        select(User.User).where(
            (User.User.username == user_create.username)
            | (User.User.email == user_create.email)
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    user = User.User(**user_create.model_dump())
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


@router.put("")
def edit_user(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_user)],
    user_edit: UserSchema.UserInDB,
    db: Annotated[Session, Depends(get_db)],
):
    db_user = db.execute(
        select(User.User).where(User.User.user_id == user_edit.user_id)
    ).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")

    db_user[0].username = user_edit.username
    db_user[0].email = user_edit.email
    db_user[0].disabled = user_edit.disabled
    db_user[0].role_id = user_edit.role_id
    if user_edit.password != "":
        db_user[0].password = get_password_hash(user_edit.password)

    db.add(db_user[0])
    db.commit()
    db.refresh(db_user[0])
    return "User updated successfully"


@router.delete("/{user_id}")
def delete_user_by_user_id(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_user)],
    user_id: str,
    db: Annotated[Session, Depends(get_db)],
):
    existing_user = db.execute(
        select(User.User).where(User.User.user_id == user_id)
    ).first()

    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    existing_user = existing_user[0]

    db.execute(
        delete(PasswordToken.PasswordToken).where(
            PasswordToken.PasswordToken.user_id == user_id
        )
    )

    db.delete(existing_user)
    db.commit()

    return "User Deleted successfully"


def get_user_by_email(email: str, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.execute(
        select(User.User).where(User.User.email == email)
    ).first()

    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    return existing_user[0]


def add_password_reset_token(user_id, token, expiry_date, db):
    password_token = PasswordToken.PasswordToken()
    password_token.user_id = user_id
    password_token.token = token
    password_token.expiry_date = expiry_date

    try:
        db.add(password_token)
        db.commit()
        db.refresh(password_token)
        return 1
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        )


def verify_reset_token(token, db):

    existing_password_token = db.execute(
        select(PasswordToken.PasswordToken).where(
            PasswordToken.PasswordToken.token == token
        )
    ).first()

    if existing_password_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="existing_password_token not found",
        )

    if existing_password_token[0].expiry_date < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expired",
        )

    return existing_password_token[0]


def update_user_password(user_id, new_password, db):
    db_user = db.execute(select(User.User).where(User.User.user_id == user_id)).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="user not found")

    if new_password != "":
        db_user[0].password = get_password_hash(new_password)

    db.add(db_user[0])
    db.commit()
    db.refresh(db_user[0])
    return "Password updated successfully"


def delete_password_token(token_id, db):
    existing_password_token = db.execute(
        select(PasswordToken.PasswordToken).where(
            PasswordToken.PasswordToken.token_id == token_id
        )
    ).first()

    if existing_password_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password Token not found",
        )

    db.delete(existing_password_token[0])
    db.commit()


def send_reset_email(email: str, token: str):
    msg = EmailMessage()
    msg.set_content(
        f"Please click on the link to reset your password: {UI_URL}/reset-password/{token}"
    )
    msg["Subject"] = "Reset Your Password"
    msg["From"] = MAIL_USERNAME
    msg["To"] = email

    with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT) as smtp:
        smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
        smtp.send_message(msg)


@router.post("/forgot-password")
def forgot_password(
    background_tasks: BackgroundTasks,
    forgot_password: ForgotPasswordSchema.ForgotPassword,
    db: Annotated[Session, Depends(get_db)],
):
    user = get_user_by_email(forgot_password.email, db)

    reset_token = secrets.token_urlsafe()

    expiry_date = datetime.utcnow() + timedelta(hours=1)

    add_password_reset_token(
        user_id=user.user_id, token=reset_token, expiry_date=expiry_date, db=db
    )

    background_tasks.add_task(send_reset_email, forgot_password.email, reset_token)
    return {
        "message": "If an account with this email was found, we've sent a link to reset your password."
    }


@router.post("/reset-password")
def reset_password(
    reset_password: ForgotPasswordSchema.ResetPassword,
    db: Annotated[Session, Depends(get_db)],
):

    existing_password_token = verify_reset_token(reset_password.token, db)

    if not existing_password_token.user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    update_user_password(
        existing_password_token.user_id, reset_password.new_password, db
    )

    delete_password_token(existing_password_token.token_id, db)

    return {"message": "Your password has been reset successfully."}
