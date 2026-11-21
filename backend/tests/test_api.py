import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_demo_auth():
    response = client.post("/api/v1/auth/demo-login")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user" in data
    assert data["user"]["email"] == "researcher@example.com"
    return data["access_token"]

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
