"""
Guardrail 4 — Policy / Advice Guardrail (after_agent, model-based).
Uses gpt-4o-mini to classify whether the draft answer crosses into
investment advice territory (UNSAFE) vs factual product information (SAFE).

Per the resource: deterministic checks run first (keyword_filter, fact_verifier).
This model-based check runs last — only for nuanced cases that rules can't catch.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import BankState

_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

SYSTEM_PROMPT = """You are a compliance officer reviewing responses from a bank's internal AI assistant.

Your job: decide if the AI's response crosses from factual information into investment advice.

SAFE (factual information the RM is allowed to share):
- Stating product features, interest rates, charges, lock-in periods
- Describing how a product works
- Listing documentation or eligibility requirements
- Sharing historical data with disclaimer
- Comparing objective product parameters (rate, tenure)

UNSAFE (investment advice that requires SEBI-registered advisor):
- Recommending a specific product for this customer
- Predicting future returns or asserting "this is a good investment"
- Suggesting asset allocation (put X% in equity, Y% in FD)
- Recommending liquidating existing investments
- Using language like "you should", "I recommend", "this is best for you"

Reply with exactly ONE word: SAFE or UNSAFE."""


def policy_guardrail(state: BankState) -> BankState:
    """
    Model-based classifier: SAFE if the draft answer is factual,
    UNSAFE if it crosses into investment advice.
    """
    flags = dict(state.get("guardrail_flags", {}))
    draft = state.get("draft_answer", "")
    transcript = state.get("transcript", "")

    if not draft:
        flags["policy_violation"] = False
        return {**state, "guardrail_flags": flags}

    user_msg = f"""RM Query: {transcript}

AI Draft Response: {draft}

Is this response SAFE (factual information) or UNSAFE (investment advice)?"""

    response = _llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_msg),
    ])

    verdict = response.content.strip().upper()
    is_unsafe = "UNSAFE" in verdict

    flags["policy_violation"] = is_unsafe
    if is_unsafe:
        flags["policy_violation_detail"] = "Response classified as investment advice by Policy Guardrail"

    return {**state, "guardrail_flags": flags}
