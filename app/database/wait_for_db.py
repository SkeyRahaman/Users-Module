# wait_for_db.py
import os
import time
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, DBAPIError

#Application Configuration
APPLICATION_NAME = os.getenv("APPLICATION_NAME","Users_Module")
# Database Configuration
DATABASE_DRIVER_SYNC = os.getenv("DATABASE_DRIVER_SYNC","sqlite")
if DATABASE_DRIVER_SYNC.startswith("sqlite"):
    DATABASE_URL_ALEMBIC = os.getenv("DATABASE_URL_ALEMBIC",f"sqlite:///./{APPLICATION_NAME}.db")
else:
    DATABASE_USERNAME = os.getenv("DATABASE_USERNAME","user")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD","password")
    DATABASE_HOST = os.getenv("DATABASE_HOST","localhost")
    DATABASE_PORT = os.getenv("DATABASE_PORT","5432")
    DATABASE_URL_ALEMBIC = os.getenv("DATABASE_URL_ALEMBIC",f"{DATABASE_DRIVER_SYNC}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{APPLICATION_NAME}")

RETRIES = int(os.environ.get("DB_WAIT_RETRIES", "60"))
DELAY = float(os.environ.get("DB_WAIT_DELAY", "1"))

# print(os.get)
if not DATABASE_URL_ALEMBIC:
    print("DATABASE_URL not set", file=sys.stderr)
    sys.exit(1)

def wait_for_db(url: str, retries: int = RETRIES, delay: float = DELAY) -> None:
    print(f"Waiting for DB from host - '{DATABASE_HOST}' at port - '{DATABASE_PORT}'...")
    engine = create_engine(url)
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database reachable")
            return
        except (OperationalError, DBAPIError) as exc:
            print(f"DB not ready ({attempt}/{retries}): {exc}")
            time.sleep(delay)
    print("Timed out waiting for DB", file=sys.stderr)
    sys.exit(2)

if __name__ == "__main__":
    wait_for_db(DATABASE_URL_ALEMBIC)
