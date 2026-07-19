import os

class Config:
    #Application Configuration
    APPLICATION_NAME = os.getenv("APPLICATION_NAME","Users_Module")
    VERSION = os.getenv("VERSION","V1")
    URL_PREFIX = os.getenv("URL_PREFIX","")
    DEFAULT_USER_ROLE_VALIDITY = 30
    DEFAULT_USER_GROUP_VALIDITY = 30
    DEFAULT_GROUP_ROLE_VALIDITY = 30

    # Database Configuration
    DATABASE_DRIVER = os.getenv("DATABASE_DRIVER","sqlite+aiosqlite")
    DATABASE_DRIVER_SYNC = os.getenv("DATABASE_DRIVER_SYNC","sqlite")
    DATABASE_USERNAME = os.getenv("DATABASE_USERNAME","user")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD","password")
    DATABASE_HOST = os.getenv("DATABASE_HOST","localhost")
    DATABASE_PORT = os.getenv("DATABASE_PORT","5432")
    if DATABASE_DRIVER.startswith("sqlite"):
        DATABASE_URL = os.getenv("DATABASE_URL",f"sqlite+aiosqlite:///./{APPLICATION_NAME}.db")
        DATABASE_URL_ALEMBIC = os.getenv("DATABASE_URL_ALEMBIC",f"sqlite:///./{APPLICATION_NAME}.db")
    else:
        DATABASE_URL = os.getenv("DATABASE_URL",f"{DATABASE_DRIVER}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{APPLICATION_NAME}")
        DATABASE_URL_ALEMBIC = os.getenv("DATABASE_URL_ALEMBIC",f"{DATABASE_DRIVER_SYNC}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{APPLICATION_NAME}")
    
    #TOKEN Configuration
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES",30)
    REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS",30)
    SECRET_KEY = os.getenv("SECRET_KEY","Some random secret key")
    TOKEN_ALGORITHM = os.getenv("TOKEN_ALGORITHM","HS256")
    PASSWORD_REST_TOKEN_EXPIRE_HOURS = int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_HOURS",1))

    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILENAME = os.getenv("LOG_FILENAME", f"{APPLICATION_NAME}.log")
    LOG_FOLDERNAME = os.getenv("LOG_FOLDERNAME", "logs")
    LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 5_000_000))
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 2))

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
