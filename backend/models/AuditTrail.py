from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone


class AuditTrail(Base):
    __tablename__ = "audit_trail"
    audit_trail_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False)
    ip_address = Column(String(255), nullable=False)
    action = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    query_params = Column(String(255))
    auth_mode = Column(String(255))
    timestamp = Column(DateTime, default = datetime.now(timezone.utc), nullable=False)

    def __init__(self, username, ip_address, action, method, query_params, auth_mode):
        self.username = username
        self.ip_address = ip_address
        self.action = action
        self.method = method
        self.query_params = query_params
        self.auth_mode = auth_mode