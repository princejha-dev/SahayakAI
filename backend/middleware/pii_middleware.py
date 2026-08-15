"""
Guardrail 2 — PII redaction middleware.
Applied to both INPUT (transcript) and OUTPUT (draft_answer).
Redacts account numbers, email addresses, and phone numbers.
"""
import re
from agents.state import BankState

_PII_PATTERNS = [
    # Account/card numbers (10-18 digits)
    (re.compile(r"\b\d{10,18}\b"), "[ACCOUNT_NUMBER_REDACTED]"),
    # Email addresses
    (re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"), "[EMAIL_REDACTED]"),
    # Indian mobile numbers
    (re.compile(r"\b[6-9]\d{9}\b"), "[PHONE_REDACTED]"),
    # PAN card format (AAAAA1234A)
    (re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"), "[PAN_REDACTED]"),
    # Aadhaar (12-digit, sometimes spaced as XXXX XXXX XXXX)
    (re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b"), "[AADHAAR_REDACTED]"),
]


def _redact(text: str) -> tuple[str, bool]:
    """Returns (redacted_text, was_pii_found)."""
    found = False
    for pattern, replacement in _PII_PATTERNS:
        new_text = pattern.sub(replacement, text)
        if new_text != text:
            found = True
            text = new_text
    return text, found


def pii_middleware(state: BankState) -> BankState:
    """
    Redacts PII from transcript (input) and draft_answer (output).
    Sets guardrail_flags['pii_detected'] = True if any PII was found.
    """
    flags = dict(state.get("guardrail_flags", {}))

    clean_transcript, input_pii = _redact(state.get("transcript", ""))
    clean_draft, output_pii = _redact(state.get("draft_answer", ""))

    flags["pii_detected"] = input_pii or output_pii or flags.get("pii_detected", False)

    return {
        **state,
        "transcript": clean_transcript,
        "draft_answer": clean_draft,
        "guardrail_flags": flags,
    }
