from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from db import get_db

router = APIRouter(prefix="/query", tags=["query"])

import json
import uuid
import os
import io
from openai import OpenAI
from fastapi.responses import StreamingResponse
from agents.graph import pipeline


class QueryRequest(BaseModel):
    transcript: str
    rm_id: str


@router.post("")
async def run_query(req: QueryRequest, db: Session = Depends(get_db)):
    """
    Runs the full LangGraph pipeline, persists output to queries/escalations,
    records detailed audit logs, and returns the result.
    """
    # 1. Run the LangGraph pipeline
    initial_state = {
        "transcript": req.transcript,
        "rm_id": req.rm_id,
        "intent": "",
        "retrieved_chunks": [],
        "draft_answer": "",
        "guardrail_flags": {},
        "confidence": 0.0,
        "status": "",
        "final_answer": "",
        "escalation_reason": None,
    }

    try:
        result = pipeline.invoke(initial_state)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LangGraph pipeline failed: {str(e)}"
        )

    query_id = str(uuid.uuid4())

    # 2. Insert query record
    db.execute(text("""
        INSERT INTO queries (
            id, rm_id, transcript, intent, retrieved_chunks, 
            draft_answer, guardrail_flags, confidence_score, 
            status, final_answer
        ) VALUES (
            :id, :rm_id, :transcript, :intent, :retrieved_chunks, 
            :draft_answer, :guardrail_flags, :confidence_score, 
            :status, :final_answer
        )
    """), {
        "id": query_id,
        "rm_id": req.rm_id,
        "transcript": result["transcript"],
        "intent": result["intent"],
        "retrieved_chunks": json.dumps(result["retrieved_chunks"]),
        "draft_answer": result["draft_answer"],
        "guardrail_flags": json.dumps(result["guardrail_flags"]),
        "confidence_score": result["confidence"],
        "status": result["status"],
        "final_answer": result["final_answer"],
    })

    # 3. Handle escalation
    if result["status"] == "escalated":
        db.execute(text("""
            INSERT INTO escalations (query_id, reason, status)
            VALUES (:query_id, :reason, 'pending')
        """), {
            "query_id": query_id,
            "reason": result["escalation_reason"] or "Low confidence or guardrail flag",
        })

    # 4. Record step-by-step audit logs
    audit_steps = [
        ("intent", {"intent": result["intent"]}),
        ("rag", {"chunks": result["retrieved_chunks"]}),
        ("guardrail", {"flags": result["guardrail_flags"]}),
        ("confidence", {"score": result["confidence"], "status": result["status"]}),
    ]

    if result["status"] == "escalated":
        audit_steps.append(("escalation", {"reason": result["escalation_reason"]}))

    for step_name, step_detail in audit_steps:
        db.execute(text("""
            INSERT INTO audit_log (query_id, step, detail)
            VALUES (:query_id, :step_name, :step_detail)
        """), {
            "query_id": query_id,
            "step_name": step_name,
            "step_detail": json.dumps(step_detail),
        })

    db.commit()

    citations = []
    if result["status"] == "safe":
        citations = [c["title"] for c in result["retrieved_chunks"]]

    return {
        "query_id": query_id,
        "status": result["status"],
        "final_answer": result["final_answer"],
        "escalation_reason": result["escalation_reason"],
        "confidence": result["confidence"],
        "guardrail_flags": result["guardrail_flags"],
        "citations": citations,
    }


class TTSRequest(BaseModel):
    text: str


@router.post("/tts")
async def text_to_speech(req: TTSRequest):
    """
    Converts text to speech using OpenAI tts-1 model and streams the MP3 audio.
    """
    try:
        openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=req.text
        )
        return StreamingResponse(io.BytesIO(response.content), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")


