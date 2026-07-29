from fastapi import FastAPI

from app.database.database import engine
from app.database.base import Base

from app.api.users import router as user_router
from app.api.rules import router as rule_router
from app.api.verdicts import router as verdict_router
from app.api.dashboard import router as dashboard_router
from app.api.connectors import router as connector_router
from app.api.validator import router as validator_router
from app.api import auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CyBreach Validator API"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all database tables
Base.metadata.create_all(bind=engine)

# Register routers
app.include_router(user_router)
app.include_router(rule_router)
app.include_router(verdict_router)
app.include_router(dashboard_router)
app.include_router(connector_router)
app.include_router(validator_router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Backend is working"}


@app.get("/health")
def health():
    return {"status": "ok"}