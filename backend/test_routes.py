from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_headers():
    login_resp = client.post("/api/auth/login", json={"email": "admin@agroflow.com", "password": "Admin@AgroFlow2026!"})
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_supported_locations():
    headers = get_auth_headers()
    response = client.get("/api/routes/locations", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 5
    names = [loc["name"] for loc in data]
    assert "Ratnagiri" in names
    assert "Pune" in names
    assert "Mumbai" in names
    print("test_get_supported_locations passed!")


def test_optimize_route_success():
    headers = get_auth_headers()
    payload = {
        "stops": [
            {"name": "Ratnagiri"},
            {"name": "Pune"},
            {"name": "Mumbai"},
            {"name": "Navi Mumbai"}
        ],
        "start_location_index": 0
    }
    response = client.post("/api/routes/optimize", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert "optimized_route" in data
    assert len(data["optimized_route"]) == 4
    assert "total_distance_km" in data
    assert data["total_distance_km"] > 0
    assert "estimated_duration_minutes" in data
    assert "legs" in data
    assert len(data["legs"]) == 3
    assert data["algorithm"] == "Google OR-Tools TSP Solver (Path Cheapest Arc)"

    print("test_optimize_route_success passed!")
    print("Optimized route response summary:", {
        "total_distance_km": data["total_distance_km"],
        "estimated_duration_formatted": data["estimated_duration_formatted"],
        "stops": [s["name"] for s in data["optimized_route"]],
        "legs": data["legs"]
    })


def test_optimize_route_custom_coordinates():
    headers = get_auth_headers()
    payload = {
        "stops": [
            {"name": "Custom Hub A", "latitude": 18.5204, "longitude": 73.8567},
            {"name": "Custom Hub B", "latitude": 19.0760, "longitude": 72.8777},
            {"name": "Custom Hub C", "latitude": 19.2183, "longitude": 72.9781}
        ]
    }
    response = client.post("/api/routes/optimize", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["optimized_route"]) == 3
    print("test_optimize_route_custom_coordinates passed!")


def test_optimize_route_insufficient_stops():
    headers = get_auth_headers()
    payload = {
        "stops": [
            {"name": "Pune"}
        ]
    }
    response = client.post("/api/routes/optimize", json=payload, headers=headers)
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "At least 2 delivery stops are required" in detail
    print("test_optimize_route_insufficient_stops passed!")


def test_optimize_route_invalid_location():
    headers = get_auth_headers()
    payload = {
        "stops": [
            {"name": "Unknown Atlantis City"},
            {"name": "Pune"}
        ]
    }
    response = client.post("/api/routes/optimize", json=payload, headers=headers)
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "could not be resolved" in detail
    print("test_optimize_route_invalid_location passed!")


if __name__ == "__main__":
    test_get_supported_locations()
    test_optimize_route_success()
    test_optimize_route_custom_coordinates()
    test_optimize_route_insufficient_stops()
    test_optimize_route_invalid_location()
    print("\nALL ROUTE OPTIMIZATION BACKEND TESTS PASSED SUCCESSFULLY!")
