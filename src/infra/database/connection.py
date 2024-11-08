from contextlib import contextmanager
from os import getenv, path
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv

DATABASE_URL = getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False)

Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

metadata = MetaData()


@contextmanager
def GET_DEFAULT_SESSION_CONTEXT():
    session = Session()
    try:
        yield session
    except Exception as e:
        raise e
    finally:
        session.close()


def get_session():
    return Session()
