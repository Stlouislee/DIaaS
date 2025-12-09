import pytest
import requests
import uuid
import os

BASE_URL = os.getenv("API_URL", "https://di.060712.qzz.io")
API_KEY = os.getenv("API_KEY")

@pytest.fixture(scope="module")
def headers():
    # If API_KEY is not set, we'll need to register a user first
    if not API_KEY:
        r = requests.post(f"{BASE_URL}/api/v1/users/register")
        assert r.status_code == 200, f"Registration failed: {r.text}"
        data = r.json()
        return {"X-API-Key": data["api_key"]}
    return {"X-API-Key": API_KEY}

def test_health_check():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_create_and_delete_session(headers):
    # Test Create Session (The bug we fixed)
    session_data = {
        "name": f"Test Session {uuid.uuid4()}",
        "description": "Integration test session"
    }
    r = requests.post(f"{BASE_URL}/api/v1/sessions/", json=session_data, headers=headers)
    assert r.status_code == 201, f"Create Session failed: {r.text}"
    session = r.json()
    session_id = session["id"]
    assert session["name"] == session_data["name"]
    assert session["tabular_datasets"] == []
    assert session["graph_datasets"] == []

    # Test Get Session
    r = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}", headers=headers)
    assert r.status_code == 200
    assert r.json()["id"] == session_id

    # Test Delete Session
    r = requests.delete(f"{BASE_URL}/api/v1/sessions/{session_id}", headers=headers)
    assert r.status_code == 204

    # Verify Deletion
    r = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}", headers=headers)
    assert r.status_code == 404
