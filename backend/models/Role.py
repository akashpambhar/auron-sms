from sqlalchemy import Column, Integer, String
from database import Base


class Role(Base):
    __tablename__ = "role"
    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String)
