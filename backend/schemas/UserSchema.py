from pydantic import BaseModel
from typing import Union


class UserBase(BaseModel):
    username: str
    email: str
    disabled: Union[bool, None] = None
    role_id: int

    class Config:
        from_attributes = True


class User(UserBase):
    user_id: int


class UserCreate(UserBase):
    password: str

class UserInDB(User):
    password: str

class UserSignIn(BaseModel):
    username: str
    password: str

class UserSignUp(UserSignIn):
    email: str