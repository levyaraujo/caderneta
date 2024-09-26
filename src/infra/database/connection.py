from os import getenv
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine, auto_begin=True)

metadata = MetaData()


def get_session():
    session = Session()
    try:
        yield session
    finally:
        session.close()
