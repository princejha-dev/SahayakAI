"""
draft_node — generates a grounded answer using ONLY the retrieved KB chunks.
Cites chunk titles. Must not hallucinate beyond the context provided.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import BankState

_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

SYSTEM_PROMPT = """You are SahayakAI, an internal assistant for bank Relationship Managers (RMs).
Your job is to answer the RM's query using ONLY the provided knowledge base excerpts.

Rules:
1. Answer factually and concisely — 2 to 5 sentences maximum.
2. Cite the source of each fact using the format [Source: <title>].
3. If the retrieved context does not contain enough information to answer, say: "The knowledge base does not have specific information on this. Please consult the relevant department."
4. Do NOT make up rates, figures, or policies not present in the context.
5. Do NOT give investment advice or recommendations — only state facts.
6. Never mention the customer directly; this answer is for the RM's reference only."""


def _build_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant knowledge base entries found."
    parts = []
    for c in chunks:
        parts.append(f"--- [{c['title']}] (similarity: {c['similarity']:.2f}) ---\n{c['content']}")
    return "\n\n".join(parts)


def draft_node(state: BankState) -> BankState:
    context = _build_context(state["retrieved_chunks"])
    user_msg = f"""RM Query: {state["transcript"]}

Knowledge Base Context:
{context}

Provide a factual, cited answer for the RM based strictly on the above context."""

    response = _llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_msg),
    ])
    return {**state, "draft_answer": response.content.strip()}
