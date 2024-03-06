import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
# from pymemcache.client import base
from database import Base, engine
from database import get_db
from routers import auth, sms, sms2, sms3, users, auth_ldap

Base.metadata.create_all(bind=engine)

# mc = base.Client((os.getenv("MC_SERVER"), 11211))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(auth_ldap.router)
app.include_router(sms.router)
app.include_router(sms2.router)
app.include_router(sms3.router)
app.include_router(users.router)

oauth2_scheme = auth.get_auth_scheme()


@app.get("/")
def server_health():
    return {"message": "Server is running"}


@app.get("/get_all_databases")
def get_all_databases(db: Session = Depends(get_db)):
    query = text("SELECT name FROM sys.databases")
    results = db.execute(query).fetchall()
    databases = [result[0] for result in results]
    return databases
