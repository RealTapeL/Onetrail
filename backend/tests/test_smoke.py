from fastapi.testclient import TestClient

from app.main import app


def test_health_check() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_empty_catalog_has_no_fake_data() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/routes")
    assert response.status_code == 200
    assert response.json() == []


def test_recommendation_refuses_to_invent_external_data() -> None:
    with TestClient(app) as client:
        client.post(
            "/api/v1/auth/register",
            json={"email": "planner@example.com", "password": "a-secure-password", "display_name": "Planner"},
        )
        token = client.post(
            "/api/v1/auth/login",
            json={"email": "planner@example.com", "password": "a-secure-password"},
        ).json()["access_token"]
        response = client.post(
            "/api/v1/recommendations/plan",
            headers={"Authorization": f"Bearer {token}"},
            json={"travel_date": "2026-08-03", "latitude": 31.2, "longitude": 121.5},
        )
    assert response.status_code == 424
