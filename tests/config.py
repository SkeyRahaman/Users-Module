from app.config import Config
import os


class TestConfig(Config):

    # Logging Configuration
    TEST_LOG_LEVEL = os.getenv("TEST_LOG_LEVEL", Config.LOG_LEVEL)
    TEST_LOG_FILENAME = os.getenv("TEST_LOG_FILENAME", Config.LOG_FILENAME)
    TEST_LOG_FOLDERNAME = os.getenv("TEST_LOG_FOLDERNAME", f"{Config.LOG_FOLDERNAME}-TEST")
    TEST_LOG_MAX_BYTES = int(os.getenv("TEST_LOG_MAX_BYTES", Config.LOG_MAX_BYTES))
    TEST_LOG_BACKUP_COUNT = int(os.getenv("TEST_LOG_BACKUP_COUNT", Config.LOG_BACKUP_COUNT))
