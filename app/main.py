from fastapi import FastAPI
from .database import Base
from .database import engine
from datetime import datetime,timezone
from app.config import Config
from app.api.routers import users, auth, permissions, groups, roles

app = FastAPI(
    title="Users Module",
    description="Endpoints related to users authentications and authorizations.",
    version=Config.VERSION
)
Base.metadata.create_all(engine)

app.include_router(users.router)
app.include_router(auth.router)
# app.include_router(permissions.router)
# app.include_router(groups.router)
# app.include_router(roles.router)


@app.get(f"{Config.URL_PREFIX}/health", name="health")
async def health_check():
    return {
            "status": "HEALTHY",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "version": Config.VERSION
        }