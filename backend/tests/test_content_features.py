from fastapi.testclient import TestClient

from app.main import app

PASSWORD = "a-secure-password"


def _auth_headers(client: TestClient, email: str) -> dict[str, str]:
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, "display_name": email.split("@")[0]},
    )
    token = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": PASSWORD},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _create_route(client: TestClient, headers: dict[str, str], **overrides) -> str:
    payload = {
        "title": "测试路线",
        "description": "一条用于自动化测试的路线",
        "region": "测试区域",
        "start_latitude": 31.2,
        "start_longitude": 121.5,
        "distance_km": 8.0,
        "elevation_gain_m": 400,
        "estimated_duration_min": 240,
        "difficulty": "moderate",
        "tags": [{"name": "溪谷", "category": "terrain", "safety_note": "雨后涉水路段湿滑"}],
    }
    payload.update(overrides)
    response = client.post("/api/v1/routes", headers=headers, json=payload)
    assert response.status_code == 201
    return response.json()["id"]


def test_route_detail_includes_archive_and_impression_stats() -> None:
    with TestClient(app) as client:
        headers = _auth_headers(client, "archive@example.com")
        route_id = _create_route(client, headers, suitable_for="有一定体能基础的进阶徒步者")
        for rating, tags in ((5, ["出片", "故事"]), (3, ["出片"])):
            response = client.post(
                f"/api/v1/routes/{route_id}/reviews",
                headers=headers,
                json={"rating": rating, "content": "测试评价", "impression_tags": tags},
            )
            assert response.status_code == 201
        detail = client.get(f"/api/v1/routes/{route_id}").json()
    assert detail["suitable_for"] == "有一定体能基础的进阶徒步者"
    assert detail["average_rating"] == 4.0
    assert detail["review_count"] == 2
    assert detail["impression_stats"][0] == {"tag": "出片", "count": 2}
    assert {stat["tag"] for stat in detail["impression_stats"]} == {"出片", "故事"}


def test_route_search_matches_description() -> None:
    with TestClient(app) as client:
        headers = _auth_headers(client, "searcher@example.com")
        _create_route(client, headers, title="普通标题", description="沿途有罕见的银叶树林")
        response = client.get("/api/v1/routes", params={"query": "银叶树"})
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_route_favorite_lifecycle() -> None:
    with TestClient(app) as client:
        headers = _auth_headers(client, "collector@example.com")
        route_id = _create_route(client, headers)

        assert client.post(f"/api/v1/routes/{route_id}/favorite", headers=headers).status_code == 201
        assert client.post(f"/api/v1/routes/{route_id}/favorite", headers=headers).status_code == 200

        favorites = client.get("/api/v1/routes/favorites/mine", headers=headers)
        assert favorites.status_code == 200
        assert any(route["id"] == route_id for route in favorites.json())

        assert client.delete(f"/api/v1/routes/{route_id}/favorite", headers=headers).status_code == 204
        assert client.delete(f"/api/v1/routes/{route_id}/favorite", headers=headers).status_code == 404

        assert client.post(f"/api/v1/routes/{route_id}/favorite").status_code == 401


def test_equipment_review_aggregation() -> None:
    with TestClient(app) as client:
        headers = _auth_headers(client, "gear@example.com")
        created = client.post(
            "/api/v1/equipment",
            headers=headers,
            json={
                "name": "测试徒步鞋",
                "category": "footwear",
                "brand": "测试品牌",
                "price_cny": 599.0,
                "weight_g": 780.0,
                "specifications": {"防水": True},
                "suitable_scenarios": ["溪谷"],
            },
        )
        assert created.status_code == 201
        equipment_id = created.json()["id"]

        for rating in (5, 3):
            response = client.post(
                f"/api/v1/equipment/{equipment_id}/reviews",
                headers=headers,
                json={"rating": rating, "content": "实测反馈"},
            )
            assert response.status_code == 201

        reviews = client.get(f"/api/v1/equipment/{equipment_id}/reviews")
        assert reviews.status_code == 200
        assert len(reviews.json()) == 2

        detail = client.get(f"/api/v1/equipment/{equipment_id}").json()
        assert detail["average_rating"] == 4.0
        assert detail["review_count"] == 2

        assert client.post(
            "/api/v1/equipment/non-existent-id/reviews",
            headers=headers,
            json={"rating": 5},
        ).status_code == 404
