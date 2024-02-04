from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    disabled = Column(Boolean, default=False)
    role_id = Column(Integer, ForeignKey("role.role_id"), default=3)

    role = relationship("Role")
