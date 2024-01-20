from pydantic import BaseModel


class RoleBase(BaseModel):
    role_name: str

    class Config:
        orm_mode = True


class Role(RoleBase):
    role_id: int
