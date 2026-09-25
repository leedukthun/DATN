from fastapi.testclient import TestClient

from app.main import app


def _auth_headers(client: TestClient) -> dict[str, str]:
    username = "pytest_user"
    password = "secret12"
    register = client.post("/api/auth/register", json={"username": username, "password": password})
    if register.status_code == 409:
        login = client.post("/api/auth/login", json={"username": username, "password": password})
        assert login.status_code == 200
        token = login.json()["access_token"]
    else:
        assert register.status_code == 201
        token = register.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_project_location_crud_smoke() -> None:
    client = TestClient(app)
    headers = _auth_headers(client)
    project_name = "Pytest Project"
    existing = client.get("/api/projects", headers=headers).json()
    for item in existing:
        if item["name"] == project_name:
            client.delete(f"/api/projects/{item['id']}", headers=headers)

    project_response = client.post(
        "/api/projects",
        json={"name": project_name, "description": "smoke"},
        headers=headers,
    )
    assert project_response.status_code == 201
    project = project_response.json()

    rename_response = client.put(
        f"/api/projects/{project['id']}",
        json={"name": "Pytest Project Renamed", "description": "updated"},
        headers=headers,
    )
    assert rename_response.status_code == 200
    assert rename_response.json()["name"] == "Pytest Project Renamed"

    location_response = client.post(
        f"/api/projects/{project['id']}/locations",
        json={"name": "Pytest Location", "description": "camera"},
        headers=headers,
    )
    assert location_response.status_code == 201
    location = location_response.json()

    stats = client.get(f"/api/locations/{location['id']}/statistics", headers=headers)
    assert stats.status_code == 200
    assert stats.json()["total_sessions"] == 0

    assert client.delete(f"/api/projects/{project['id']}", headers=headers).status_code == 204


def test_register_and_login() -> None:
    client = TestClient(app)
    username = "pytest_auth_user"
    password = "secret12"
    client.post("/api/auth/register", json={"username": username, "password": password})
    login = client.post("/api/auth/login", json={"username": username, "password": password})
    assert login.status_code == 200
    token = login.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == username
    blocked = client.get("/api/projects")
    assert blocked.status_code == 401
