from fastapi import Depends, APIRouter, HTTPException, status
from database import SessionLocal
from typing import Annotated
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from schemas import UserSchema
from models import User
from sqlalchemy import select

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

@router.get("/")
async def get_users(db: Annotated[Session, Depends(get_db)]):
    results = db.execute(select(User.User)).fetchall()
    users = [result[0] for result in results]
    return users

@router.post("/")
async def add_user(
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

@router.put("/")
async def edit_user(user_edit: UserSchema.UserInDB, db: Annotated[Session, Depends(get_db)]):
    with SessionLocal() as session:
        db_user = session.get(User, user_edit.user_id)
        
        if not db_user:
            raise HTTPException(status_code=404, detail="user not found")
    
        temp_user = User.User(**user_edit.model_dump())

        for key, value in temp_user.items():
            setattr(db_user, key, value)

        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
   

# @app.patch("/heroes/{hero_id}", response_model=HeroRead)
# def update_hero(hero_id: int, hero: HeroUpdate):
#     with SessionLocal() as session:
#         db_hero = session.get(Hero, hero_id)
#         if not db_hero:
#             raise HTTPException(status_code=404, detail="Hero not found")
#         hero_data = hero.model_dump(exclude_unset=True)
#         for key, value in hero_data.items():
#             setattr(db_hero, key, value)
#         session.add(db_hero)
#         session.commit()
#         session.refresh(db_hero)
#         return db_hero