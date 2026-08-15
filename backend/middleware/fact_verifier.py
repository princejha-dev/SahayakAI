"""
Guardrail 3 — Fact Verifier (after_agent style, deterministic first).
Extracts numbers from draft_answer and verifies they exist in retrieved chunks.
If a number in the answer isn't in ANY retrieved chunk → flag mismatch.
"""
import re
from agents.state import BankState


def _extract_numbers(text: str) -> set[str]:
    """Extract all standalone numbers and percentages from text."""
    # Match percentages (6.80%), plain numbers (40,000), decimals (0.50)
    return set(re.findall(r"\d+(?:[.,]\d+)*(?:%)?", text))


def fact_verifier(state: BankState) -> BankState:
    """
    Deterministic check: every numeric claim in draft_answer must appear
    in at least one retrieved chunk. Mismatches are flagged.
    """
    flags = dict(state.get("guardrail_flags", {}))
    draft = state.get("draft_answer", "")
    chunks = state.get("retrieved_chunks", [])

    if not draft or not chunks:
        flags["fact_mismatch"] = False
        return {**state, "guardrail_flags": flags}

    # Build full text of all retrieved chunks
    chunk_text = " ".join(c.get("content", "") for c in chunks)

    answer_numbers = _extract_numbers(draft)
    chunk_numbers = _extract_numbers(chunk_text)

    # Find numbers in the answer that don't appear in any chunk
    mismatched = answer_numbers - chunk_numbers

    # Filter out trivial numbers (1, 2, 3, single digits) — too common
    significant_mismatches = {n for n in mismatched if len(n.replace(",", "").replace(".", "")) > 1}

    if significant_mismatches:
        flags["fact_mismatch"] = True
        flags["fact_mismatch_detail"] = f"Unverified numbers in answer: {', '.join(significant_mismatches)}"
    else:
        flags["fact_mismatch"] = False

    return {**state, "guardrail_flags": flags}
