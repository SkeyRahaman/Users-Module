from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.config import Config
from app.api.dependencies.database import get_db
from datetime import datetime, timezone
import os
from app.database.models import engine, Base
from alembic.config import Config as AlembicConfig
from alembic import command

router = APIRouter(
    tags=["Health"]
)

# Record the moment this module was first imported (≈ server start time)
_SERVER_START: datetime = datetime.now(timezone.utc)


def _uptime_str(start: datetime) -> str:
    """Return a human-readable 'up for X days Y hours Z minutes' string."""
    delta = datetime.now(timezone.utc) - start
    total_seconds = int(delta.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m")
    return " ".join(parts)


@router.get(f"{Config.URL_PREFIX}/health", name="health")
async def health_check():
    return {
            "status": "HEALTHY",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "version": Config.VERSION
        }


@router.get(f"{Config.URL_PREFIX}/api-status", name="api_status")
async def api_status(db: AsyncSession = Depends(get_db)):
    """
    Extended status check.
    - Runs SELECT 1 to verify the database is reachable.
    - Returns up_from with a human-readable server uptime string.
    """
    db_ok = False
    db_error = None
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:
        db_error = str(exc)

    return {
        "status": "HEALTHY" if db_ok else "DEGRADED",
        "database": "up" if db_ok else "down",
        "db_error": db_error,
        "up_from": _uptime_str(_SERVER_START),
        "server_start": _SERVER_START.isoformat().replace("+00:00", "Z"),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "version": Config.VERSION,
    }


@router.post(f"{Config.URL_PREFIX}/reset-db", name="reset_db")
async def reset_db():
    """
    Completely reset the database by deleting the SQLite database file
    (or dropping all tables if using a non-SQLite database like PostgreSQL)
    and running all Alembic migrations from scratch to seed default data.
    """
    try:
        # 1. Dispose engine connections to avoid database locks
        await engine.dispose()

        # 2. Check if SQLite and delete the database files
        db_path = None
        if Config.DATABASE_DRIVER.startswith("sqlite") or Config.DATABASE_URL.startswith("sqlite"):
            url = Config.DATABASE_URL
            for prefix in ["sqlite+aiosqlite:///", "sqlite:///"]:
                if url.startswith(prefix):
                    db_path = url[len(prefix):]
                    break

        if db_path:
            db_path = os.path.abspath(db_path)
            for suffix in ["", "-shm", "-wal"]:
                p = db_path + suffix
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass
        else:
            # If not SQLite, drop all tables (e.g. Postgres)
            async with engine.begin() as conn:
                await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
                await conn.run_sync(Base.metadata.drop_all)

        # 3. Run migrations programmatically
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))

        original_cwd = os.getcwd()
        try:
            os.chdir(backend_root)
            alembic_cfg = AlembicConfig("alembic.ini")
            command.upgrade(alembic_cfg, "head")
        finally:
            os.chdir(original_cwd)

        # 4. Dispose engine again to clean up migration connections
        await engine.dispose()

        return {"status": "SUCCESS", "message": "Database reset completed successfully"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database reset failed: {str(exc)}")