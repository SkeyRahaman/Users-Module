import os

class Config:
    URL_PREFIX = os.getenv("URL_PREFIX","")
    VERSION = os.getenv("VERSION","V1")
    DATABASE_URL = os.getenv("DATABASE_URL","sqlite:///./mydatabase.db")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30)
    SECRET_KEY = os.getenv("SECRET_KEY","Some random secret key")
    TOKEN_ALGORITHM = os.getenv("TOKEN_ALGORITHM","HS256")


    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL","sqlite+aiosqlite:///./test.db")
    