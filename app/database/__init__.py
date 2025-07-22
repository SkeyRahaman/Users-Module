from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import Config

engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, autocommit = False, bind=engine)

Base = declarative_base()

#tables
from .associations import *
from .group import Group
from .permission import Permission
from .role import Role
from .user import User

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        