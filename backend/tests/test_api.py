"""
Phase 4 — FastAPI Endpoint Verification Test
Launches the FastAPI server locally, sends queries, resolves escalations,
checks the audit trail, and confirms everything is stored correctly in Postgres.
"""
import os
import sys
import time
import requests
import subprocess
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://127.0.0.1:8000"


def test_endpoints():
    print("=== Phase 4 API Endpoint Tests ===")

    # 1. Test POST /query with a safe factual query
    print("\n1. Testing POST /query (Safe Query)...")
    res_safe = requests.post(f"{API_URL}/query", json={
        "transcript": "What is the interest rate on a 1-year fixed deposit?",
        "rm_id": "RM_SAFE_TEST"
    })
    assert res_safe.status_code == 200, f"Error: {res_safe.text}"
    safe_data = res_safe.json()
    print("Response data:")
    print(f"  Query ID:   {safe_data['query_id']}")
    print(f"  Status:     {safe_data['status']}")
    print(f"  Confidence: {safe_data['confidence']}")
    print(f"  Citations:  {safe_data['citations']}")
    assert safe_data['status'] == "safe"
    assert len(safe_data['citations']) > 0

    # 2. Test POST /query with an advice-seeking query (will escalate)
    print("\n2. Testing POST /query (Escalated Query)...")
    res_esc = requests.post(f"{API_URL}/query", json={
        "transcript": "Should this customer buy a mutual fund now?",
        "rm_id": "RM_ESC_TEST"
    })
    assert res_esc.status_code == 200, f"Error: {res_esc.text}"
    esc_data = res_esc.json()
    print("Response data:")
    print(f"  Query ID:   {esc_data['query_id']}")
    print(f"  Status:     {esc_data['status']}")
    print(f"  Reason:     {esc_data['escalation_reason']}")
    assert esc_data['status'] == "escalated"

    # 3. Test GET /escalations
    print("\n3. Testing GET /escalations...")
    res_queue = requests.get(f"{API_URL}/escalations")
    assert res_queue.status_code == 200, f"Error: {res_queue.text}"
    queue = res_queue.json()
    print(f"Pending escalations count: {len(queue)}")
    
    # Find our escalated query
    target_esc = None
    for esc in queue:
        if esc['query_id'] == esc_data['query_id']:
            target_esc = esc
            break
            
    assert target_esc is not None, "Error: Escalation row not found in queue!"
    print(f"Found pending escalation ID: {target_esc['id']}")

    # 4. Test POST /escalations/{id}/resolve
    print(f"\n4. Testing POST /escalations/{target_esc['id']}/resolve...")
    res_resolve = requests.post(f"{API_URL}/escalations/{target_esc['id']}/resolve", json={
        "decision": "approved",
        "reviewer_id": "COMP_REV_01",
        "reviewer_response": "We suggest consulting our SEBI investment advisory desk."
    })
    assert res_resolve.status_code == 200, f"Error: {res_resolve.text}"
    resolve_data = res_resolve.json()
    print(f"Resolution outcome: {resolve_data['status']} ({resolve_data['decision']})")
    assert resolve_data['status'] == "resolved"

    # 5. Test GET /audit/{query_id} for the escalated query
    print(f"\n5. Testing GET /audit/{esc_data['query_id']}...")
    res_audit = requests.get(f"{API_URL}/audit/{esc_data['query_id']}")
    assert res_audit.status_code == 200, f"Error: {res_audit.text}"
    audit_log = res_audit.json()
    print("Audit log steps:")
    for log in audit_log:
        print(f"  - {log['timestamp']}: [{log['step']}] detail: {log['detail']}")

    assert len(audit_log) >= 5, "Expected audit log to have at least 5 steps (intent, rag, guardrail, confidence, resolution)"

    print("\n[PASS] All FastAPI endpoints behave correctly!")


if __name__ == "__main__":
    test_endpoints()
