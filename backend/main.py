from fastapi import FastAPI, Depends, HTTPException
import json
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
import pymssql
from pymemcache.client import base

load_dotenv()

mc = base.Client((os.getenv("MC_SERVER"), 11211))

SQL_DB = os.getenv("SQL_DB")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_SERVER = os.getenv("SQL_SERVER")

app = FastAPI()

connection_string = f"mssql+pymssql://{SQL_USER}:{SQL_PASSWORD}@{SQL_SERVER}/{SQL_DB}"
engine = create_engine(
    connection_string,
    creator=lambda: pymssql.connect(SQL_SERVER, SQL_USER, SQL_PASSWORD, SQL_DB),
)


def get_db():
    db = Session(autocommit=False, autoflush=False, bind=engine)
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


@app.get("/get_all_databases_cached")
async def get_all_databases_chached():
    return get_dbs()


@app.get("/get_all_databases")
async def get_all_databases(db: Session = Depends(get_db)):
    query = text("SELECT name FROM sys.databases")
    results = db.execute(query).fetchall()
    databases = [result[0] for result in results]
    return databases
