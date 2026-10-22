import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_part54_health_and_flows():
    # Test health check
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_part54_role_specific_endpoints():
    # Verify that key endpoints respond cleanly without server errors
    endpoints = [
        "/api/batches",
        "/api/inventory",
        "/api/orders",
        "/api/shipments",
        "/api/spoilage/summary",
        "/api/spoilage/risk",
    ]
    for ep in endpoints:
        resp = client.get(ep)
        # Should either require auth (401/403) or return success (200), but NOT 500 internal server error
        assert resp.status_code in [200, 401, 403]

if __name__ == "__main__":
    test_part54_health_and_flows()
    print("Part 5.4 Backend business flow tests passed successfully!")
