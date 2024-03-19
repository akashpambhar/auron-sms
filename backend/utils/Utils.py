import os
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from models import AuditTrail
from database import SessionLocal
from sqlalchemy.exc import IntegrityError

ENUM_DATABASE = "database"
ENUM_ACTIVE_DIRECTORY = "active_directory"

SECRET_KEY = os.getenv("SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# SERVER
LDAP_HOST = os.getenv("LDAP_HOST")
LDAP_PORT = os.getenv("LDAP_PORT")
LDAP_DOMAIN = os.getenv("LDAP_DOMAIN")
LDAP_USE_SSL = os.getenv("LDAP_USE_SSL")
LDAP_START_TLS = os.getenv("LDAP_START_TLS")
LDAP_SSL_SKIP_VERIFY = os.getenv("LDAP_SSL_SKIP_VERIFY")
LDAP_BIND_DN = os.getenv("LDAP_BIND_DN")
LDAP_BIND_PASSWORD = os.getenv("LDAP_BIND_PASSWORD")
LDAP_SEARCH_FILTER = os.getenv("LDAP_SEARCH_FILTER")
LDAP_SEARCH_BASE_DNS = os.getenv("LDAP_SEARCH_BASE_DNS")

# SERVER GROUP MAPPINGS
LDAP_ADMINS_GROUP = os.getenv("LDAP_ADMINS_GROUP")
LDAP_USERS_GROUP = os.getenv("LDAP_USERS_GROUP")
LDAP_OTHERS_GROUP = os.getenv("LDAP_OTHERS_GROUP")

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

def get_list_from_env(key, delimiter=","):
    value = os.getenv(key)
    if value:
        return value.split(delimiter)
    else:
        return []
    
def decode_jwt(token):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        auth_mode: str = payload.get("auth_mode")
        if username is None or auth_mode is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    return (username, auth_mode)

def insert_audit_trail(ip_address, path, method, query_params, username, auth_mode):
    audit_trail = AuditTrail.AuditTrail(username, ip_address, path, method, query_params, auth_mode)
    db = SessionLocal()
    try:
        db.add(audit_trail)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving audit trail: {str(e)}",
        )
    finally:
        db.close()