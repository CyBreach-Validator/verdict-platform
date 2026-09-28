import json

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.contracts.verdict_event import build_verdict_event
from app.kafka.producer import publish_corrected_verdict
from app.models.verdict import Verdict


def build_verdict_payload(
    action_id,
    verdict: str,
    confidence,
    causal_chain,
    mttd_seconds,
    matched_evidence_ref,
    regulatory_control_refs,
) -> dict:
    """The single v2.0 serializer. Kafka, WebSocket, REST and the DB row all
    derive from this, so the four emit paths can no longer disagree."""

    return build_verdict_event(
        action_id=action_id,
        verdict=verdict,
        confidence=confidence,
        causal_chain=causal_chain,
        mttd_seconds=mttd_seconds,
        matched_evidence_ref=matched_evidence_ref,
        regulatory_control_refs=regulatory_control_refs,
    )


def save_verdict(
    db: Session,
    action_id: str,
    rule_id: str,
    rule_name: str,
    verdict: str,
    confidence,
    event: dict,
    causal_chain=None,
    mttd_seconds=None,
    matched_evidence_ref=None,
    regulatory_control_refs=None,
):
    """Persist a verdict and return both the ORM row and the canonical v2.0
    payload it was stored from.

    N-D11: the caller reuses that one `payload` for its WebSocket broadcast, its
    Kafka publish and its REST response, so those three transports are
    byte-identical by construction rather than by three parallel hand-builds.
    """

    payload = build_verdict_payload(
        action_id=action_id,
        verdict=verdict,
        confidence=confidence,
        causal_chain=causal_chain,
        mttd_seconds=mttd_seconds,
        matched_evidence_ref=matched_evidence_ref,
        regulatory_control_refs=regulatory_control_refs,
    )

    db_verdict = Verdict(
        action_id=payload["action_id"],
        rule_id=rule_id,
        rule_name=rule_name,
        verdict=payload["verdict"],
        confidence=payload["confidence"],
        causal_chain=payload["causal_chain"],
        mttd_seconds=payload["mttd_seconds"],
        matched_evidence_ref=payload["matched_evidence_ref"],
        regulatory_control_refs=payload["regulatory_control_refs"],
        event_data=json.dumps(event, sort_keys=True),
        content_hash=payload["content_hash"],
        is_superseded=False,
        superseded_by=None
    )

    try:
        db.add(db_verdict)
        db.commit()
    except IntegrityError:
        # N-D13: a current verdict with this exact contract hash already
        # exists. That is a client re-submitting the same evidence, not a
        # server fault, so return the stored row instead of raising a 500.
        # Re-deriving `payload` rather than returning it keeps the response
        # byte-identical to the row that is actually in the database.
        db.rollback()
        existing = (
            db.query(Verdict)
            .filter(Verdict.content_hash == payload["content_hash"])
            .filter(Verdict.is_superseded.is_(False))
            .first()
        )
        if existing is None:
            # The violation came from some other constraint; do not mask it.
            raise
        return existing, get_verdict_payload(existing)

    db.refresh(db_verdict)

    return db_verdict, payload


def get_verdict_payload(verdict: Verdict) -> dict:
    """Rebuild the v2.0 payload from a stored row (for REST/WebSocket replies)."""

    return build_verdict_payload(
        action_id=verdict.action_id,
        verdict=verdict.verdict,
        confidence=verdict.confidence,
        causal_chain=verdict.causal_chain or [],
        mttd_seconds=verdict.mttd_seconds,
        matched_evidence_ref=verdict.matched_evidence_ref,
        regulatory_control_refs=verdict.regulatory_control_refs or [],
    )


def get_all_verdicts(db: Session):
    return db.query(Verdict).all()


def get_verdict_by_id(db: Session, verdict_id: int):
    return db.query(Verdict).filter(Verdict.id == verdict_id).first()


def get_verdicts_by_rule(db: Session, rule_id: str):
    return db.query(Verdict).filter(Verdict.rule_id == rule_id).all()


def get_verdicts_by_action(db: Session, action_id: str):
    """Look up every verdict for one evidence action.

    B4: verdicts are now joinable to an ingested rule across pods by the
    canonical string `rule_id` and by `action_id`, instead of a hardcoded id.
    """

    return (
        db.query(Verdict)
        .filter(Verdict.action_id == action_id)
        .order_by(Verdict.created_at.asc())
        .all()
    )


def correct_verdict(
    db: Session,
    verdict_id: int,
    new_verdict: str,
    causal_chain=None,
    confidence=None,
):
    old_verdict = (
        db.query(Verdict)
        .filter(Verdict.id == verdict_id)
        .first()
    )

    if not old_verdict:
        return None, None

    payload = build_verdict_payload(
        action_id=old_verdict.action_id,
        verdict=new_verdict,
        confidence=old_verdict.confidence if confidence is None else confidence,
        causal_chain=old_verdict.causal_chain if causal_chain is None else causal_chain,
        mttd_seconds=old_verdict.mttd_seconds,
        matched_evidence_ref=old_verdict.matched_evidence_ref,
        regulatory_control_refs=old_verdict.regulatory_control_refs or [],
    )

    # N-D13: retire the old row before inserting its replacement. See the
    # matching note in `revalidation_service.revalidate_verdict` -- the partial
    # unique index covers only current rows, and SQLAlchemy would otherwise emit
    # the INSERT before the UPDATE.
    old_verdict.is_superseded = True
    db.commit()

    corrected_verdict = Verdict(
        action_id=old_verdict.action_id,
        rule_id=old_verdict.rule_id,
        rule_name=old_verdict.rule_name,
        verdict=payload["verdict"],
        confidence=payload["confidence"],
        causal_chain=payload["causal_chain"],
        mttd_seconds=payload["mttd_seconds"],
        matched_evidence_ref=payload["matched_evidence_ref"],
        regulatory_control_refs=payload["regulatory_control_refs"],
        event_data=old_verdict.event_data,
        content_hash=payload["content_hash"],
        is_superseded=False,
        superseded_by=None
    )

    try:
        db.add(corrected_verdict)
        db.commit()
    except Exception:
        db.rollback()
        # Restore the original as the current verdict rather than leaving the
        # action_id with a superseded row and no live replacement.
        old_verdict.is_superseded = False
        db.commit()
        raise

    db.refresh(corrected_verdict)

    old_verdict.superseded_by = corrected_verdict.id

    db.commit()
    db.refresh(old_verdict)

    publish_corrected_verdict(payload)

    return corrected_verdict, payload
