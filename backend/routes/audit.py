from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from db import get_db

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/{query_id}")
async def get_audit_log(query_id: str, db: Session = Depends(get_db)):
    """Returns the full step-by-step audit trail for a query."""
    rows = db.execute(text("""
        SELECT id, query_id, step, detail, timestamp
        FROM audit_log
        WHERE query_id = :query_id
        ORDER BY timestamp ASC
    """), {"query_id": query_id}).mappings().all()

    if not rows:
        raise HTTPException(status_code=404, detail="No audit logs found for this query")

    return [dict(row) for row in rows]
