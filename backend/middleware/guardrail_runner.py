"""
guardrail_runner.py — Orchestrates all 4 guardrail layers in correct order.

Order (per golden rule: deterministic first, model-based second):
  1. keyword_filter   (before_agent, deterministic, zero LLM cost)
  2. pii_middleware   (deterministic, redacts input + output)
  3. fact_verifier    (after_agent, deterministic number matching)
  4. policy_guardrail (after_agent, model-based SAFE/UNSAFE classifier)

This is used as a single LangGraph node inserted between draft_node and confidence_node.
"""
from agents.state import BankState
from middleware.keyword_filter import keyword_filter
from middleware.pii_middleware import pii_middleware
from middleware.fact_verifier import fact_verifier
from middleware.policy_guardrail import policy_guardrail


def input_guardrail_node(state: BankState) -> BankState:
    """
    Runs input-level deterministic guardrails before intent and RAG.
    Redacts input PII and blocks off-topic/harmful keywords early.
    """
    # Initialize guardrail flags if not present
    if "guardrail_flags" not in state or state["guardrail_flags"] is None:
        state["guardrail_flags"] = {}

    # Layer 1: Keyword filter (deterministic, zero LLM cost)
    state = keyword_filter(state)
    if state.get("status") == "escalated":
        return state

    # Layer 2: PII redaction on transcript (input)
    state = pii_middleware(state)
    return state


def output_guardrail_node(state: BankState) -> BankState:
    """
    Runs output-level guardrails after drafting.
    Redacts output PII, verifies numbers, and runs model-based policy checks.
    """
    # Layer 3: PII redaction on draft_answer (output)
    state = pii_middleware(state)

    # Layer 4: Fact verifier (deterministic number matching)
    state = fact_verifier(state)

    # Layer 5: Policy guardrail (model-based advice check)
    state = policy_guardrail(state)

    return state

