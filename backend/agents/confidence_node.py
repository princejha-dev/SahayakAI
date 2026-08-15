"""
confidence_node — computes a confidence score and decides whether to speak or escalate.

Phase 2 scoring (simple, no guardrails yet):
  - Base score = average similarity of retrieved chunks (0.0 – 1.0)
  - Penalise if intent is advice_seeking or account_specific (-0.5)
  - Penalise if no chunks retrieved (-0.4)
  - Penalise each guardrail flag that is True (-0.2 each) — wired properly in Phase 3

Threshold: confidence >= 0.5 → safe, else → escalate
"""
from agents.state import BankState

SAFE_THRESHOLD = 0.45


def confidence_node(state: BankState) -> BankState:
    chunks = state.get("retrieved_chunks", [])
    intent = state.get("intent", "factual")
    flags = state.get("guardrail_flags", {})

    # Base: max similarity (top chunk) — most relevant chunk is the signal,
    # not the average which gets diluted by lower-ranked chunks.
    if chunks:
        base_score = max(c["similarity"] for c in chunks)
    else:
        base_score = 0.0

    score = base_score

    # Intent penalty
    if intent in ("advice_seeking", "account_specific"):
        score -= 0.50

    # No-retrieval penalty
    if not chunks:
        score -= 0.40

    # Guardrail flag penalties — only hard violations reduce confidence.
    # pii_detected is informational (redaction happened, not a risk).
    # fact_mismatch_detail is a string label, not a bool — skip it.
    PENALTY_FLAGS = ("keyword_blocked", "fact_mismatch", "policy_violation")
    for flag_name in PENALTY_FLAGS:
        if flags.get(flag_name):
            score -= 0.20

    score = max(0.0, min(1.0, score))  # clamp to [0, 1]

    if score >= SAFE_THRESHOLD:
        status = "safe"
        escalation_reason = None
        final_answer = state.get("draft_answer", "")
    else:
        status = "escalated"
        # Build escalation reason
        reasons = []
        if intent == "advice_seeking":
            reasons.append("Query classified as investment advice (not permitted for RMs)")
        if intent == "account_specific":
            reasons.append("Query requires access to specific customer account data")
        if not chunks:
            reasons.append("No relevant knowledge base content found")
        # Only report hard violation flags (not informational ones like pii_detected, detail strings)
        REPORT_FLAGS = ("keyword_blocked", "fact_mismatch", "policy_violation")
        for flag_name in REPORT_FLAGS:
            if flags.get(flag_name):
                detail = flags.get(f"{flag_name}_detail", "")
                msg = f"Guardrail flagged: {flag_name}"
                if detail:
                    msg += f" — {detail}"
                reasons.append(msg)
        if not reasons:
            reasons.append(f"Low confidence score: {score:.2f}")
        escalation_reason = "; ".join(reasons)
        final_answer = ""

    return {
        **state,
        "confidence": round(score, 4),
        "status": status,
        "final_answer": final_answer,
        "escalation_reason": escalation_reason,
    }
