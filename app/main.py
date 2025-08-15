from fastapi import FastAPI
from app.database.models import Base, engine
from app.config import Config
from app.api.routers import users, auth, permissions, groups, roles, health
from app.database.models import create_db_and_tables
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app : FastAPI):
    # Code before yield runs at startup
    await create_db_and_tables()
    yield
    # Code after yield runs at shutdown

app = FastAPI(
    title="Users Module",
    description="Endpoints related to users authentications and authorizations.",
    version=Config.VERSION,
    lifespan=lifespan
)

app.include_router(health.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(permissions.router)
app.include_router(groups.router)
app.include_router(roles.router)
