from pydantic import BaseModel


class RoleBase(BaseModel):
    role_name: str

    class Config:
        from_attributes = True


class Role(RoleBase):
    role_id: int
