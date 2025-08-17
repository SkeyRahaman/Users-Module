import os

class Config:
    URL_PREFIX = os.getenv("URL_PREFIX","")
    VERSION = os.getenv("VERSION","V1")
    DATABASE_URL = os.getenv("DATABASE_URL","sqlite+aiosqlite:///./mydatabase.db")
    DATABASE_URL_ALEMBIC = os.getenv("DATABASE_URL","sqlite:///./mydatabase.db")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30)
    SECRET_KEY = os.getenv("SECRET_KEY","Some random secret key")
    TOKEN_ALGORITHM = os.getenv("TOKEN_ALGORITHM","HS256")

    # Add Admin user default info
    ADMIN_USER = {
        "firstname": os.getenv("ADMIN_FIRSTNAME", "Admin"),
        "middlename": os.getenv("ADMIN_MIDDLENAME", None),
        "lastname": os.getenv("ADMIN_LASTNAME", "User"),
        "username": os.getenv("ADMIN_USERNAME", "admin"),
        "email": os.getenv("ADMIN_EMAIL", "admin@example.com"),
        "password_hash": os.getenv("ADMIN_PASSWORD_HASH", "$2b$12$NeWF6NuJfn4y.0Mp.iN3qenyKYQr5Z.kEjBo38669wJuQ81bRSfia"),  # adminpassword
        "is_verified": True,
        "is_active": True,
        "is_deleted": False,
    }

    # Add Normal user default info
    NORMAL_USER = {
        "firstname": os.getenv("USER_FIRSTNAME", "Regular"),
        "middlename": os.getenv("USER_MIDDLENAME", None),
        "lastname": os.getenv("USER_LASTNAME", "User"),
        "username": os.getenv("USER_USERNAME", "user"),
        "email": os.getenv("USER_EMAIL", "user@example.com"),
        "password_hash": os.getenv("USER_PASSWORD_HASH", "$2b$12$fmyx9k0b2zvzfSB71TwwIOZGvu6hAEeHzJqWtPsX6IvDnuBZiAyAK"),  #userpasswrd
        "is_verified": True,
        "is_active": True,
        "is_deleted": False,
    }



    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL","sqlite+aiosqlite:///./test.db")

    DEFAULT_USER_ROLE_VALIDITY = 30
    DEFAULT_USER_GROUP_VALIDITY = 30
    DEFAULT_GROUP_ROLE_VALIDITY = 30

    TEST_USER = {
        "firstname": "test_firstname",
        "lastname": "test_lastname",
        "username": "test_username",
        "email": "test1@email.com",
        "password": "password1",
    }
