from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import engine, verify_schema

from app.api.users import router as user_router
from app.api.rules import router as rule_router
from app.api.verdicts import router as verdict_router
from app.api.dashboard import router as dashboard_router
from app.api.connectors import router as connector_router
from app.api.validator import router as validator_router
from app.api.audit_logs import router as audit_logs_router
from app.api import auth

from app.security.security import verify_access_token

from app.websocket.connection_manager import manager

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.middleware.rate_limit import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """N-D2: refuse to serve against an unmigrated database.

    The import-time `Base.metadata.create_all()` this replaces would build a
    schema from the models, which is not the schema the migrations produce --
    so a broken migration chain stayed invisible until someone compared the two.
    Checking at startup makes the mismatch loud and immediate.
    """

    verify_schema(engine)
    yield


app = FastAPI(
    title="CyBreach Validator API",
    lifespan=lifespan,
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

app.include_router(user_router, prefix="/api/v2")
app.include_router(rule_router, prefix="/api/v2")
app.include_router(verdict_router, prefix="/api/v2")
app.include_router(dashboard_router, prefix="/api/v2")
app.include_router(connector_router, prefix="/api/v2")
app.include_router(validator_router, prefix="/api/v2")
app.include_router(audit_logs_router, prefix="/api/v2")
app.include_router(auth.router, prefix="/api/v2")


@app.websocket("/ws/verdicts")
async def websocket_endpoint(websocket: WebSocket):
    """Live verdict feed for the dashboard.

    B11: this socket is not listed in the OpenAPI schema, so the auth-coverage
    test cannot see it -- it was an anonymous read of every verdict the platform
    produces, which is exactly what the REST guards were added to prevent.

    The browser `WebSocket` constructor cannot attach an `Authorization` header,
    so the token arrives as a query parameter. It is deliberately never logged:
    query strings land in access logs and proxy logs, which would put a live
    bearer token in the same place a token must never be.
    """

    token = websocket.query_params.get("token")

    try:
        verify_access_token(token)
    except HTTPException:
        # 1008 = policy violation. Reject before `accept()` so the socket never
        # joins the broadcast set.
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)

    try:
        while True:
            message = await websocket.receive_text()

            # The client's text is not logged: it is untrusted input, and
            # writing it verbatim to stdout is a log-injection vector.
            await websocket.send_json(
                {
                    "type": "heartbeat",
                    "message": "Connection Successful",
                }
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/")
def root():
    return {"message": "Backend is working"}


@app.get("/health")
def health():
    # Liveness only: it must not touch the database, so an orchestrator can use
    # it as a container healthcheck without a database round trip. Schema
    # currency is a startup concern (`verify_schema`), not a per-request one.
    return {"status": "ok", "service": "verdict-platform"}
