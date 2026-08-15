"""
BankState — the shared state dict that flows through every LangGraph node.
"""
from typing import TypedDict, Optional


class BankState(TypedDict):
    transcript: str
    rm_id: str
    intent: str                       # 'factual' | 'advice_seeking' | 'account_specific'
    retrieved_chunks: list[dict]      # [{title, category, content, similarity}, ...]
    draft_answer: str
    guardrail_flags: dict             # populated in Phase 3
    confidence: float                 # 0.0 – 1.0
    status: str                       # 'safe' | 'escalated'
    final_answer: str
    escalation_reason: Optional[str]
