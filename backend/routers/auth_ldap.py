from fastapi import APIRouter
import os
from ldap3 import Server, Connection, ALL, SUBTREE

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

    results = []

    # with Connection(server, LDAP_BIND_DN, LDAP_BIND_PASSWORD, auto_bind=True) as conn:
    # # Search for user's roles or group memberships
    #     conn.search(search_base=LDAP_SEARCH_BASE_DNS,
    #                 search_filter=f'(uid={username})',
    #                 attributes=['sn'])
        
    #     results = str(conn.entries)
    #     # roles = [entry['cn'].value for entry in conn.entries]
    

    # return results
    
    # if 'admin' in roles:
    #     print("User has admin role.")
    # else:
    #     print("User roles:", roles)

    conn.search(LDAP_SEARCH_BASE_DNS, f'(uid={username})', SUBTREE, attributes=['sn'])

    if not conn.entries:
        print("User not found.")
    else:
        user_dn = conn.entries[0].entry_dn
        results.append(user_dn)
        print(user_dn)
        user_roles = [] 

        user_conn = Connection(server, user_dn, password)
        if user_conn.bind():
            print("Authentication successful.")
            results.append("Authentication Success")
            

            # for group_dn in conn.entries[0].entry_dn:
            #     print(group_dn)
            # if 'cn=admin,' in str(user_dn):
            #     user_roles.append('admin')
            # elif 'cn=user,' in str(user_dn):
            #     user_roles.append('user')
            # print("User roles:", user_roles)
            
        else:
            print("Authentication failed.")
            results.append("Authentication failed")
        
        user_conn.unbind()

    conn.unbind()

    return str(results)
