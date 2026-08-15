"""
intent_node — classifies the RM's query into one of three intents:
  - factual        : asking for a rate, feature, policy fact (RM can answer)
  - advice_seeking : asking what the customer *should* do (must escalate)
  - account_specific: asking about a specific customer account (must escalate)
"""
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import BankState

_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

SYSTEM_PROMPT = """You are an intent classifier for a bank's internal RM assistant.
Classify the query into exactly one of these three intents:
- factual: asking for product features, interest rates, charges, eligibility criteria, documentation, or process steps
- advice_seeking: asking what a customer should invest in, whether to buy/sell/switch a product, or seeking personalised recommendations
- account_specific: asking about a specific customer's account balance, transaction history, or personal account details

Respond with ONLY the intent label. No explanation. One of: factual, advice_seeking, account_specific"""


def intent_node(state: BankState) -> BankState:
    response = _llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=state["transcript"]),
    ])
    intent = response.content.strip().lower()
    # Sanitise — default to factual if unexpected output
    if intent not in ("factual", "advice_seeking", "account_specific"):
        intent = "factual"
    return {**state, "intent": intent}
