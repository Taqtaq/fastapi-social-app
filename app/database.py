from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .config import settings


SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@\
{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# try:
#     conn = psycopg2.connect(host='localhost', database='fastapi', 
#                     user='postgres', password='0141',
#                     cursor_factory=RealDictCursor, client_encoding='UTF8')
#     cursor = conn.cursor()
#     print("Database conection was succesfull!")
# except Exception as error:
#     print("Connecting to database failde")
#     print("Error: ", error)
#     time.sleep(2)
