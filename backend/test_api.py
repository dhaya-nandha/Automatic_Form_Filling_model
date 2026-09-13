import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_api_routes():
    print("Testing FastAPI API routes...")

    # 1. Test Root
    res = client.get("/")
    assert res.status_code == 200, f"Root endpoint failed: {res.text}"
    print("  - Root endpoint: OK")

    # 2. Test Profile Retrieval
    res = client.get("/api/profile")
    assert res.status_code == 200, f"Profile endpoint failed: {res.text}"
    print(f"  - Profile endpoint: OK (Found {len(res.json())} profile fields)")

    # 3. Test Form Field Matching Endpoint
    match_payload = {
        "target_form": "http://example.com/form",
        "fields": [
            {"field_id": "fname", "label": "Full Name", "field_type": "text"},
            {"field_id": "email_input", "label": "Email Address", "field_type": "email"}
        ]
    }
    res = client.post("/api/match-fields", json=match_payload)
    assert res.status_code == 200, f"Match fields failed: {res.text}"
    data = res.json()
    assert "matches" in data
    print("  - Match fields endpoint: OK")

    print("[SUCCESS] All API route tests passed!")

if __name__ == "__main__":
    test_api_routes()
