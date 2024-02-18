from fastapi import Depends, APIRouter, HTTPException, status
from database import SessionLocal
from typing import Annotated
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from schemas import UserSchema
from models import User, Role
from routers import auth
from sqlalchemy import select, join, text

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/users", tags=["users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_password_hash(password):
    return pwd_context.hash(password)


@router.get("")
async def get_users(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_user)],
    db: Annotated[Session, Depends(get_db)]
):
    join_condition = User.User.role_id == Role.Role.role_id
    query = select(User.User).select_from(join(User.User, Role.Role, join_condition)).where(User.User.username != current_user.username and User.User.role_id != 1)

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
async def get_user_by_user_id(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_user)],
    user_id: str, db: Annotated[Session, Depends(get_db)]
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
async def get_user_by_user_username(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_user)],
    username: str, db: Annotated[Session, Depends(get_db)]
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
async def add_user(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_user)],
    user_create: UserSchema.UserCreate, db: Annotated[Session, Depends(get_db)]
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
async def edit_user(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_user)],
    user_edit: UserSchema.UserInDB, db: Annotated[Session, Depends(get_db)]
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
async def delete_user_by_user_id(
    current_user: Annotated[UserSchema.User, Depends(auth.get_current_admin_user)],
    user_id: str, db: Annotated[Session, Depends(get_db)]
):
    existing_user = db.execute(
        select(User.User).where(User.User.user_id == user_id)
    ).first()[0]

    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )
    
    db.delete(existing_user)
    db.commit()

    return "User Deleted successfully"