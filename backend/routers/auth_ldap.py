from fastapi import APIRouter
import os
from ldap3 import Server, Connection, ALL

router = APIRouter(prefix="/auth/ldap", tags=["auth/ldap"])

# SERVER
LDAP_HOST = os.getenv("LDAP_HOST")
LDAP_PORT = os.getenv("LDAP_PORT")
LDAP_USE_SSL = os.getenv("LDAP_USE_SSL")
LDAP_START_TLS = os.getenv("LDAP_START_TLS")
LDAP_SSL_SKIP_VERIFY = os.getenv("LDAP_SSL_SKIP_VERIFY")
LDAP_BIND_DN = os.getenv("LDAP_BIND_DN")
LDAP_BIND_PASSWORD = os.getenv("LDAP_BIND_PASSWORD")
LDAP_SEARCH_FILTER = os.getenv("LDAP_SEARCH_FILTER")
LDAP_SEARCH_BASE_DNS = os.getenv("LDAP_SEARCH_BASE_DNS")

# SERVER ATTRIBUTES
LDAP_NAME = os.getenv("LDAP_NAME")
LDAP_SURNAME = os.getenv("LDAP_SURNAME")
LDAP_USERNAME = os.getenv("LDAP_USERNAME")
LDAP_MEMBER_OF = os.getenv("LDAP_MEMBER_OF")
LDAP_EMAIL = os.getenv("LDAP_EMAIL")

# SERVER GROUP MAPPINGS
LDAP_GROUP_DN = os.getenv("LDAP_GROUP_DN")
LDAP_ORG_ROLE = os.getenv("LDAP_ORG_ROLE")

# ldap_server = 'localhost'
# bind_dn = 'cn=admin,dc=adiths,dc=com'
# bind_password = 'admin'
# search_base = 'dc=adiths,dc=com' 
# search_filter = '(objectClass=person)' 

@router.get("/test")
def ldap():
    server = Server(LDAP_HOST, get_info=ALL)
    try:
        with Connection(server, LDAP_BIND_DN, LDAP_BIND_PASSWORD, auto_bind=True) as conn:
            conn.search(LDAP_SEARCH_BASE_DNS, LDAP_SEARCH_FILTER, attributes=['sn'])
            result = []
            for entry in conn.entries:
                print(entry)
                result.append(entry)
        print(result)
        return str(result)
    except Exception as e:
        print(f"An error occurred: {e}")

@router.get("/login")
def login(
    username : str = None,
    password: str = None
):
    server = Server(LDAP_HOST, get_info=ALL)
    conn = Connection(server, LDAP_BIND_DN, LDAP_BIND_PASSWORD, auto_bind=True)

    # Search for user's roles or group memberships
    conn.search(search_base=LDAP_SEARCH_BASE_DNS,
                search_filter=f'(sAMAccountName={username})',
                attributes=[LDAP_SURNAME]) 
    roles = [entry['cn'].value for entry in conn.entries]
    
    if 'admin' in roles:
        print("User has admin role.")
    else:
        print("User roles:", roles)

    conn.unbind()