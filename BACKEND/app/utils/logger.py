from logging.handlers import RotatingFileHandler
import structlog
import logging
import os

from app.config import Config

os.makedirs(Config.LOG_FOLDERNAME, exist_ok=True)

rotating_handler = RotatingFileHandler(
    f"{Config.LOG_FOLDERNAME}/{Config.LOG_FILENAME}",
    maxBytes=Config.LOG_MAX_BYTES,
    backupCount=Config.LOG_BACKUP_COUNT,
)

# Configure logging
logging.basicConfig(
    format="%(message)s",
    level=logging._nameToLevel.get(Config.LOG_LEVEL, logging.INFO),
    handlers=[
        rotating_handler,
        # logging.StreamHandler(sys.stdout)
    ],
)

# Configure structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger("api")

def get_logger(name: str = __name__):
    return structlog.get_logger(name)