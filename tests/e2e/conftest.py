"""
End-to-End Test Configuration
Starts Docker Compose and runs tests against real API
"""
import pytest
import subprocess
import time
import requests
import os

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:8000")
COMPOSE_FILE = "docker-compose.yml"
STARTUP_TIMEOUT = 60  # seconds


@pytest.fixture(scope="session", autouse=True)
def docker_services():
    """Start Docker Compose services before tests and stop after"""
    print("\n🚀 Starting Docker Compose services...")
    
    # Stop any existing containers
    subprocess.run(
        ["docker", "compose", "down", "-v"],
        capture_output=True,
        check=False
    )
    
    # Start services
    result = subprocess.run(
        ["docker", "compose", "up", "-d", "--build"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Failed to start Docker Compose:\n{result.stderr}")
        pytest.exit("Failed to start Docker Compose services")
    
    print("⏳ Waiting for services to be ready...")
    
    # Wait for API to be ready
    start_time = time.time()
    while time.time() - start_time < STARTUP_TIMEOUT:
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ API is ready!")
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)
    else:
        # Cleanup on timeout
        subprocess.run(["docker", "compose", "down", "-v"], check=False)
        pytest.exit(f"API did not become ready within {STARTUP_TIMEOUT} seconds")
    
    # Additional wait for databases
    time.sleep(5)
    
    yield
    
    # Teardown
    print("\n🛑 Stopping Docker Compose services...")
    subprocess.run(
        ["docker", "compose", "down", "-v"],
        capture_output=True,
        check=False
    )
    print("✅ Cleanup complete")


@pytest.fixture(scope="session")
def api_base_url():
    """Provide base URL for API"""
    return BASE_URL


@pytest.fixture(scope="session")
def api_key(api_base_url):
    """Register a user and get API key"""
    response = requests.post(f"{api_base_url}/api/v1/users/register")
    assert response.status_code == 200, f"Failed to register user: {response.text}"
    data = response.json()
    return data["api_key"]


@pytest.fixture
def auth_headers(api_key):
    """Provide authentication headers"""
    return {"X-API-Key": api_key}


@pytest.fixture
def session_id(api_base_url, auth_headers):
    """Create a test session and return its ID"""
    response = requests.post(
        f"{api_base_url}/api/v1/sessions/",
        json={"name": "Test Session", "description": "E2E Test"},
        headers=auth_headers
    )
    assert response.status_code == 201
    session = response.json()
    yield session["id"]
    
    # Cleanup
    requests.delete(
        f"{api_base_url}/api/v1/sessions/{session['id']}",
        headers=auth_headers
    )
