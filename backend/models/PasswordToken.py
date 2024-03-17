from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column
from database import Base


class PasswordToken(Base):
    __tablename__ = "password_token"
    token_id = mapped_column(Integer, primary_key=True, index=True)
    token = mapped_column(String, nullable=False)
    expiry_date = mapped_column(DateTime, nullable=False)
    user_id = mapped_column(Integer, ForeignKey("user.user_id"), default=3)

    user = relationship("User")
