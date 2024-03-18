import os

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

def get_list_from_env(key, delimiter=","):
    value = os.getenv(key)
    if value:
        return value.split(delimiter)
    else:
        return []
