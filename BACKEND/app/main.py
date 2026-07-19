from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Config
from app.api.routers import users, auth, permissions, groups, roles, health
from app.middlewares.logger_middlewares import LogCorrelationIdMiddleware

app = FastAPI(
    title="Users Module",
    description="Endpoints related to users authentications and authorizations.",
    version=Config.VERSION
)

app.add_middleware(LogCorrelationIdMiddleware)

# Enable CORS for frontend requests — registered last so it executes FIRST on incoming requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://skeyrahaman.github.io",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(groups.router)
app.include_router(roles.router)
app.include_router(permissions.router)
