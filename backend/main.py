import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from pymemcache.client import base
from database import engine, SessionLocal, Base
from routers import auth, sms, users

Base.metadata.create_all(bind=engine)


mc = base.Client((os.getenv("MC_SERVER"), 11211))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(sms.router)
app.include_router(users.router)

oauth2_scheme = auth.get_auth_scheme()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def load_dbs(refresh: bool = False):
    # Check if the result is already cached
    result = mc.get("database_list")
    if result is not None and not refresh:
        return
    with Session(autocommit=False, autoflush=False, bind=engine) as db:
        query = text("SELECT name FROM sys.databases")
        results = db.execute(query).fetchall()
        databases = [result[0] for result in results]
        json_dbs = json.dumps(databases, default=str)
        # Cache the result
        mc.set("database_list", json_dbs)


load_dbs()


def get_dbs():
    dbs = mc.get("database_list")
    # convert statuses to dict
    dbs = json.loads(dbs)
    return dbs


@app.get("/")
async def hello_world():
    return {"message": "Hello World"}


@app.get("/get_all_databases_cached")
async def get_all_databases_chached():
    return get_dbs()


@app.get("/get_all_databases")
async def get_all_databases(db: Session = Depends(get_db)):
    query = text("SELECT name FROM sys.databases")
    results = db.execute(query).fetchall()
    databases = [result[0] for result in results]
    return databases
