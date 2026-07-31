from fastapi import APIRouter, WebSocket, WebSocketDisconnect

print("✅ websocket.py loaded")

from app.websocket.connection_manager import manager

router = APIRouter()


@router.websocket("/ws/verdicts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    print("✅ Dashboard Connected")

    try:
        while True:
            message = await websocket.receive_text()

            print(f"Received: {message}")

            await websocket.send_json(
                {
                    "type": "heartbeat",
                    "message": "Connection Successful"
                }
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("❌ Dashboard Disconnected")