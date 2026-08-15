"""
Guardrail 1 — keyword/topic filter (before_agent style).
Runs BEFORE any LLM call. Zero cost for blocked requests.
Blocks obviously off-topic, harmful, or competitor-referencing input.
"""
import re
from agents.state import BankState

# Topics that should never reach the LLM
BLOCKED_PATTERNS = [
    r"\b(bomb|kill|hack|exploit|jailbreak|ignore previous)\b",
    r"\b(competitor|hdfc|icici|sbi|axis|kotak)\s+(rate|offer|scheme|product)\b",
    r"\b(stock tip|hot tip|buy now|guaranteed profit|crypto|bitcoin)\b",
    r"\b(aadhaar number|pan number|account (number|no))\s*[:=]\s*\d",   # PII in query
]

_PATTERNS = [re.compile(p, re.IGNORECASE) for p in BLOCKED_PATTERNS]


def keyword_filter(state: BankState) -> BankState:
    """
    Returns updated state with guardrail_flags['keyword_blocked'] = True
    if the transcript matches any blocked pattern.
    """
    transcript = state.get("transcript", "")
    flags = dict(state.get("guardrail_flags", {}))

    blocked = any(p.search(transcript) for p in _PATTERNS)
    flags["keyword_blocked"] = blocked

    if blocked:
        return {
            **state,
            "guardrail_flags": flags,
            "status": "escalated",
            "escalation_reason": "Input blocked by keyword filter (off-topic or harmful content)",
        }
    return {**state, "guardrail_flags": flags}
