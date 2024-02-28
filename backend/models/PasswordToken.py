from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class PasswordToken(Base):
    __tablename__ = "password_token"
    token_id = Column(Integer, primary_key=True, index=True)
    token = Column(String, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), default=3)

    user = relationship("User")