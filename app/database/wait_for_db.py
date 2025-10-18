# wait_for_db.py
import os
import time
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, DBAPIError

DATABASE_URL = os.getenv("DATABASE_URL_ALEMBIC",f"sqlite:///./mydatabase.db")
RETRIES = int(os.environ.get("DB_WAIT_RETRIES", "60"))
DELAY = float(os.environ.get("DB_WAIT_DELAY", "1"))

if not DATABASE_URL:
    print("DATABASE_URL not set", file=sys.stderr)
    sys.exit(1)

def wait_for_db(url: str, retries: int = RETRIES, delay: float = DELAY) -> None:
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
    wait_for_db(DATABASE_URL)
