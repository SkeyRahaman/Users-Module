from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.config import Config
from app.api.dependencies.database import get_db
from datetime import datetime, timezone

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