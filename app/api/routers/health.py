from fastapi import APIRouter
from app.config import Config
from datetime import datetime, timezone

router = APIRouter(
    tags=["Health"]
)


@router.get(f"{Config.URL_PREFIX}/health", name="health")
async def health_check():
    return {
            "status": "HEALTHY",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "version": Config.VERSION
        }