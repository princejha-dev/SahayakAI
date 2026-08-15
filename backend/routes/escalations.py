from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timezone
from db import get_db

router = APIRouter(prefix="/escalations", tags=["escalations"])


@router.get("")
async def get_escalations(db: Session = Depends(get_db)):
    """Returns all pending escalations with joined query data."""
    rows = db.execute(text("""
        SELECT
            e.id, e.query_id, e.reason, e.status, e.reviewer_id,
            e.reviewer_response, e.resolved_at,
            q.transcript, q.draft_answer, q.guardrail_flags, q.rm_id
        FROM escalations e
        JOIN queries q ON q.id = e.query_id
        WHERE e.status = 'pending'
        ORDER BY e.id DESC
    """)).mappings().all()

    return [dict(row) for row in rows]


class ResolveRequest(BaseModel):
    decision: str           # 'approved' | 'edited' | 'rejected'
    reviewer_id: str
    reviewer_response: Optional[str] = None


@router.post("/{escalation_id}/resolve")
async def resolve_escalation(
    escalation_id: str,
    req: ResolveRequest,
    db: Session = Depends(get_db),
):
    """Compliance officer resolves an escalation."""
    now = datetime.now(timezone.utc)

    # Fetch escalation to get query_id
    row = db.execute(text("""
        SELECT id, query_id FROM escalations WHERE id = :id
    """), {"id": escalation_id}).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Escalation not found")

    query_id = row["query_id"]
    final_answer = req.reviewer_response or "Approved as-is"

    # Update escalation
    db.execute(text("""
        UPDATE escalations
        SET status = :status,
            reviewer_id = :reviewer_id,
            reviewer_response = :reviewer_response,
            resolved_at = :resolved_at
        WHERE id = :id
    """), {
        "status": req.decision,
        "reviewer_id": req.reviewer_id,
        "reviewer_response": req.reviewer_response,
        "resolved_at": now,
        "id": escalation_id,
    })

    # Update query status and final answer
    db.execute(text("""
        UPDATE queries
        SET status = 'resolved', final_answer = :final_answer
        WHERE id = :query_id
    """), {"final_answer": final_answer, "query_id": str(query_id)})

    # Audit log
    import json
    db.execute(text("""
        INSERT INTO audit_log (query_id, step, detail, timestamp)
        VALUES (:query_id, 'resolution', :detail, :ts)
    """), {
        "query_id": str(query_id),
        "detail": json.dumps({
            "decision": req.decision,
            "reviewer_id": req.reviewer_id,
            "reviewer_response": req.reviewer_response,
        }),
        "ts": now,
    })

    db.commit()
    return {"status": "resolved", "decision": req.decision}
