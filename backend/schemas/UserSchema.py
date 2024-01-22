from pydantic import BaseModel
from typing import Union


class UserBase(BaseModel):
    username: str
    email: str
    disabled: Union[bool, None] = None
    role_id: int

    class Config:
        orm_mode = True


class User(UserBase):
    user_id: int


class UserCreate(UserBase):
    password: str

class UserInDB(User):
    password: str

class UserSignUp(BaseModel):
    username: str
    email: str
    password: str