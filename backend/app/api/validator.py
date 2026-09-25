from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.validator import ValidationRequest
from app.services.validator_service import validate_rule
from app.services.verdict_service import save_verdict
from app.kafka.producer import publish_verdict
from app.database.database import get_db
from app.websocket.connection_manager import manager

router = APIRouter(
    prefix="/validator",
    tags=["Validator"]
)


@router.post("/validate")
async def validate(
    request: ValidationRequest,
    db: Session = Depends(get_db)
):

    print(">>> validator.py endpoint called <<<")

    result = validate_rule(
        request.rule_query,
        request.event
    )

    # Save verdict
    saved_verdict = save_verdict(
        db=db,
        rule_id=1,
        rule_name="Suspicious PowerShell",
        verdict=result["status"],
        event=request.event
    )

    # Broadcast to all connected WebSocket clients
    await manager.broadcast(
        {
            "id": saved_verdict.id,
            "rule_id": saved_verdict.rule_id,
            "rule_name": saved_verdict.rule_name,
            "verdict": saved_verdict.verdict,
            "event_data": saved_verdict.event_data,
            "created_at": str(saved_verdict.created_at),
        }
    )

    print("📡 Verdict broadcasted")

    # Publish to Kafka
    publish_verdict({
    "action_id": request.action_id,
    "verdict": result["status"],
    "confidence": result["confidence"] / 100,
    "causal_chain": result.get("matched_fields", []),
    "mttd_seconds": None,
    "matched_evidence_ref": request.action_id,
    "regulatory_control_refs": [],
    "content_hash": saved_verdict.verdict_hash
})

    print(result)

    return result