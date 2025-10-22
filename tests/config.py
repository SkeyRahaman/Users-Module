from app.config import Config
import os


class TestConfig(Config):

    # Logging Configuration
    TEST_LOG_LEVEL = os.getenv("TEST_LOG_LEVEL", Config.LOG_LEVEL)
    TEST_LOG_FILENAME = os.getenv("TEST_LOG_FILENAME", Config.LOG_FILENAME)
    TEST_LOG_FOLDERNAME = os.getenv("TEST_LOG_FOLDERNAME", f"{Config.LOG_FOLDERNAME}-TEST")
    TEST_LOG_MAX_BYTES = int(os.getenv("TEST_LOG_MAX_BYTES", Config.LOG_MAX_BYTES))
    TEST_LOG_BACKUP_COUNT = int(os.getenv("TEST_LOG_BACKUP_COUNT", Config.LOG_BACKUP_COUNT))

    TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL",f"sqlite+aiosqlite:///./TEST-{Config.APPLICATION_NAME}.db")
    TEST_DATABASE_URL_ALEMBIC = os.getenv("TEST_DATABASE_URL_ALEMBIC",f"sqlite:///./TEST-{Config.APPLICATION_NAME}.db")
    TEST_USER = {
        "firstname": "test_firstname",
        "lastname": "test_lastname",
        "username": "test_username",
        "email": "test1@email.com",
        "password": "password1",
    }
