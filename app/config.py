import os

class Config:
    URL_PREFIX = os.getenv("URL_PREFIX","")
    VERSION = os.getenv("VERSION","V1")
    DATABASE_URL = os.getenv("DATABASE_URL","sqlite:///./mydatabase.db")


    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL","sqlite:///:memory:")
    