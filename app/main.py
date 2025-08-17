from fastapi import FastAPI
from app.config import Config
from app.api.routers import users, auth, permissions, groups, roles, health

app = FastAPI(
    title="Users Module",
    description="Endpoints related to users authentications and authorizations.",
    version=Config.VERSION
)

app.include_router(health.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(permissions.router)
app.include_router(groups.router)
app.include_router(roles.router)
