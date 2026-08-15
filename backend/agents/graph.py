"""
graph.py — Wires all nodes into a LangGraph StateGraph with full guardrail pipeline.

Flow:
  intent_node → rag_node → draft_node → guardrail_node → confidence_node
                                                               ↓
                                                    (conditional edge)
                                                   ↙              ↘
                                             speak_node      escalate_node

Observability:
  LangSmith tracing is enabled automatically when env vars are set:
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_API_KEY=<your key>
    LANGCHAIN_PROJECT=SahayakAI
  Every node invocation, LLM call, and tool use appears in the LangSmith trace.
"""
import os
from langgraph.graph import StateGraph, END
from agents.state import BankState
from agents.intent_node import intent_node
from agents.rag_node import rag_node
from agents.draft_node import draft_node
from agents.confidence_node import confidence_node
from agents.terminal_nodes import speak_node, escalate_node
from middleware.guardrail_runner import input_guardrail_node, output_guardrail_node


def _route_input(state: BankState) -> str:
    """Conditional edge: routes from input_guardrails directly to escalate if blocked, else intent."""
    return "escalate" if state.get("status") == "escalated" else "intent"


def _route(state: BankState) -> str:
    """Conditional edge: routes from confidence_node to speak or escalate."""
    return "speak" if state["status"] == "safe" else "escalate"


def build_graph():
    graph = StateGraph(BankState)

    # ── Register all nodes ────────────────────────────────────────────────────
    graph.add_node("input_guardrails", input_guardrail_node)
    graph.add_node("intent", intent_node)
    graph.add_node("rag", rag_node)
    graph.add_node("draft", draft_node)
    graph.add_node("output_guardrails", output_guardrail_node)
    graph.add_node("confidence", confidence_node)
    graph.add_node("speak", speak_node)
    graph.add_node("escalate", escalate_node)

    # ── Input Guardrail conditional routing ───────────────────────────────────
    graph.add_conditional_edges(
        "input_guardrails",
        _route_input,
        {
            "intent": "intent",
            "escalate": "escalate",
        }
    )

    # ── Linear edges ─────────────────────────────────────────────────────────
    graph.add_edge("intent", "rag")
    graph.add_edge("rag", "draft")
    graph.add_edge("draft", "output_guardrails")
    graph.add_edge("output_guardrails", "confidence")

    # ── Conditional routing from confidence ──────────────────────────────────
    graph.add_conditional_edges(
        "confidence",
        _route,
        {
            "speak": "speak",
            "escalate": "escalate",
        },
    )

    graph.add_edge("speak", END)
    graph.add_edge("escalate", END)
    graph.set_entry_point("input_guardrails")

    return graph.compile()



# Compiled graph — imported by FastAPI routes and test scripts
# LangSmith auto-traces every invocation when env vars are set
pipeline = build_graph()
