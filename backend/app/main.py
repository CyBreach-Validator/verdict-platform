from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import engine
from app.database.base import Base

from app.api.users import router as user_router
from app.api.rules import router as rule_router
from app.api.verdicts import router as verdict_router
from app.api.dashboard import router as dashboard_router
from app.api.connectors import router as connector_router
from app.api.validator import router as validator_router
from app.api.audit_logs import router as audit_logs_router
from app.api import auth

from app.websocket.connection_manager import manager

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.middleware.rate_limit import limiter

app = FastAPI(
    title="CyBreach Validator API"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(user_router)
app.include_router(rule_router)
app.include_router(verdict_router)
app.include_router(dashboard_router)
app.include_router(connector_router)
app.include_router(validator_router)
app.include_router(audit_logs_router)
app.include_router(auth.router)


@app.websocket("/ws/verdicts")
async def websocket_endpoint(websocket: WebSocket):

    print("🔥 WebSocket endpoint reached")

    await manager.connect(websocket)

    print("✅ Dashboard Connected")

    try:
        while True:
            message = await websocket.receive_text()

            print(f"Received: {message}")

            await websocket.send_json(
                {
                    "type": "heartbeat",
                    "message": "Connection Successful",
                }
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("❌ Dashboard Disconnected")


@app.get("/")
def root():
    return {"message": "Backend is working"}


@app.get("/health")
def health():
    return {"status": "ok"}