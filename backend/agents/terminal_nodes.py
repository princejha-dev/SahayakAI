"""
Terminal nodes — speak_node and escalate_node.
speak_node: finalises the safe answer (TTS triggered from frontend).
escalate_node: marks the query as escalated (row inserted in FastAPI layer).
"""
from agents.state import BankState


def speak_node(state: BankState) -> BankState:
    """Safe path — the draft_answer becomes the final answer."""
    return {
        **state,
        "status": "safe",
        "final_answer": state.get("draft_answer", ""),
    }


def escalate_node(state: BankState) -> BankState:
    """Escalation path — clears the final answer; FastAPI will write the escalation row."""
    return {
        **state,
        "status": "escalated",
        "final_answer": "",
    }
