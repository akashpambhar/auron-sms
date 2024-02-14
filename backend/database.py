from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pymssql
import os
from dotenv import load_dotenv

load_dotenv()

SQL_DB = os.getenv("SQL_DB")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")
SQL_SERVER = os.getenv("SQL_SERVER1")
SQL_PORT = os.getenv("SQL_PORT")

connection_string = f"mssql+pymssql://{SQL_USER}:{SQL_PASSWORD}@{SQL_SERVER}:{SQL_PORT}/{SQL_DB}"
engine = create_engine(
    connection_string,
    creator=lambda: pymssql.connect(SQL_SERVER, SQL_USER, SQL_PASSWORD, SQL_DB, port=SQL_PORT),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
