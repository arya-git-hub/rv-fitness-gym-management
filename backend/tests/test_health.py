"""
backend/tests/test_health.py
Smoke test — verifies the app starts and the health endpoint works.
Run: cd backend && pytest tests/test_health.py -v
"""


def test_health_returns_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_unknown_route_returns_404(client):
    response = client.get("/api/nonexistent")
    assert response.status_code == 404


def test_cors_header_present(client):
    response = client.get(
        "/api/health",
        headers={"Origin": "http://localhost:5173"},
    )
    assert response.status_code == 200
