import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "ResearchMate AI"
    assert data["status"] == "online"
    assert data["docs_url"] == "/docs"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_api_v1_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_docs_and_openapi():
    # Verify Swagger docs and openapi.json are reachable
    docs_resp = client.get("/docs")
    assert docs_resp.status_code == 200
    assert "swagger-ui" in docs_resp.text.lower() or "html" in docs_resp.text.lower()

    openapi_resp = client.get("/openapi.json")
    assert openapi_resp.status_code == 200
    schema = openapi_resp.json()
    assert schema["info"]["title"] == "ResearchMate AI"
    assert "/api/v1/auth/demo-login" in schema["paths"]
    assert "/api/v1/auth/register" in schema["paths"]
    assert "/api/v1/auth/login" in schema["paths"]
    assert "/health" in schema["paths"]

def test_demo_auth():
    response = client.post("/api/v1/auth/demo-login")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["email"] == "researcher@example.com"
    return data["access_token"]

def test_manual_register_and_login():
    unique_email = f"test_{uuid.uuid4().hex[:8]}@university.edu"
    password = "SecurePassword123!"
    full_name = "Dr. Test Researcher"

    # Register
    reg_resp = client.post("/api/v1/auth/register", json={
        "email": unique_email,
        "password": password,
        "full_name": full_name
    })
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == unique_email
    assert reg_data["user"]["full_name"] == full_name

    # Login
    login_resp = client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": password
    })
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
    assert login_data["user"]["email"] == unique_email

    # Me check
    headers = {"Authorization": f"Bearer {login_data['access_token']}"}
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == unique_email

def test_projects_crud():
    # Login
    auth_resp = client.post("/api/v1/auth/demo-login")
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # List
    list_resp = client.get("/api/v1/projects", headers=headers)
    assert list_resp.status_code == 200
    assert isinstance(list_resp.json(), list)

    # Create
    create_resp = client.post("/api/v1/projects", json={
        "name": "Automated Testing Project",
        "description": "Integration testing project for ResearchMate AI"
    }, headers=headers)
    assert create_resp.status_code == 200
    proj = create_resp.json()
    assert proj["name"] == "Automated Testing Project"

    # Get
    get_resp = client.get(f"/api/v1/projects/{proj['id']}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == proj["id"]

    # Delete
    del_resp = client.delete(f"/api/v1/projects/{proj['id']}", headers=headers)
    assert del_resp.status_code == 200

def test_analytics_dashboard():
    auth_resp = client.post("/api/v1/auth/demo-login")
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    dash_resp = client.get("/api/v1/analytics/dashboard", headers=headers)
    assert dash_resp.status_code == 200
    data = dash_resp.json()
    assert "total_papers" in data
    assert "total_projects" in data
    assert "papers_by_year" in data
    assert "status_distribution" in data
