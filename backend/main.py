from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import Base, engine
from database import get_db
from routers import auth, sms, sms2, sms3, users
from utils.Utils import decode_jwt, insert_audit_trail

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
# app.include_router(auth_ldap.router)
app.include_router(sms.router)
app.include_router(sms2.router)
app.include_router(sms3.router)
app.include_router(users.router)


@app.get("/")
def server_health():
    return {"message": "Server is running"}


@app.get("/get_all_databases")
def get_all_databases(db: Session = Depends(get_db)):
    query = text("SELECT name FROM sys.databases")
    results = db.execute(query).fetchall()
    databases = [result[0] for result in results]
    return databases

@app.get("/get-client-ip")
def get_client_ip(request: Request):
    client_ip = request.client.host
    print(request.headers)
    print(request.client)
    return str(client_ip)


@app.middleware("http")
def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        response = call_next(request)
        if all(filter_url not in request.url.__str__() for filter_url in ['docs', 'openapi.json', 'favicon.ico', 'auth/signin', 'auth/ad/signin', 'auth/signup']):
            username = None
            auth_mode = None
            if "Authorization" in request.headers:
                authorization_header = request.headers["Authorization"]
                token = authorization_header.split(" ")[1] 
                username, auth_mode = decode_jwt(token)

            insert_audit_trail(request.client.host, request.url.path, request.method, request.query_params.__str__(), username, auth_mode)
    except Exception as e:
        print(str(e))

    return response