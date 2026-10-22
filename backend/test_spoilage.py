from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.models.inventory import Inventory
from app.models.batch import Batch
from app.models.product import Product
from app.services.spoilage_service import evaluate_inventory_spoilage_risk

client = TestClient(app)


def test_spoilage_scoring_unit_cases():
    today = date.today()
    p = Product(id=99, name="Mango", category="Fruits")

    # 1. Normal / Low-Risk Inventory
    b1 = Batch(id=101, batch_code="B1-LOW", harvest_date=today - timedelta(days=2), expiry_date=today + timedelta(days=20), product=p)
    inv1 = Inventory(id=201, batch_id=101, batch=b1, temperature=12.0, humidity=60.0, warehouse_location="Test Hub", quantity=100.0)
    res1 = evaluate_inventory_spoilage_risk(inv1)
    assert res1["risk_score"] < 30
    assert res1["risk_level"] == "Low"
    assert "Normal cold chain" in res1["recommendation"]
    print("1. Low Risk Test Passed!")

    # 2. Expiry Approaching (<= 2 days)
    b2 = Batch(id=102, batch_code="B2-NEAR-EXP", harvest_date=today - timedelta(days=5), expiry_date=today + timedelta(days=2), product=p)
    inv2 = Inventory(id=202, batch_id=102, batch=b2, temperature=14.0, humidity=65.0, warehouse_location="Test Hub", quantity=100.0)
    res2 = evaluate_inventory_spoilage_risk(inv2)
    assert res2["risk_score"] >= 35
    assert any(f["factor"] == "Shelf Life" for f in res2["factors"])
    print("2. Expiry Approaching Test Passed!")

    # 3. Expired Batch
    b3 = Batch(id=103, batch_code="B3-EXPIRED", harvest_date=today - timedelta(days=15), expiry_date=today - timedelta(days=1), product=p)
    inv3 = Inventory(id=203, batch_id=103, batch=b3, temperature=14.0, humidity=65.0, warehouse_location="Test Hub", quantity=100.0)
    res3 = evaluate_inventory_spoilage_risk(inv3)
    assert res3["risk_score"] >= 50
    assert "EXPIRED" in res3["factors"][0]["message"]
    print("3. Expired Batch Test Passed!")

    # 4. High Temperature Condition (> 22°C)
    b4 = Batch(id=104, batch_code="B4-HIGH-TEMP", harvest_date=today - timedelta(days=3), expiry_date=today + timedelta(days=15), product=p)
    inv4 = Inventory(id=204, batch_id=104, batch=b4, temperature=26.5, humidity=60.0, warehouse_location="Test Hub", quantity=100.0)
    res4 = evaluate_inventory_spoilage_risk(inv4)
    assert any(f["factor"] == "Temperature" and f["impact"] == 30 for f in res4["factors"])
    print("4. High Temperature Test Passed!")

    # 5. High Humidity Condition (> 80%)
    b5 = Batch(id=105, batch_code="B5-HIGH-HUMID", harvest_date=today - timedelta(days=3), expiry_date=today + timedelta(days=15), product=p)
    inv5 = Inventory(id=205, batch_id=105, batch=b5, temperature=14.0, humidity=85.0, warehouse_location="Test Hub", quantity=100.0)
    res5 = evaluate_inventory_spoilage_risk(inv5)
    assert any(f["factor"] == "Humidity" and f["impact"] == 15 for f in res5["factors"])
    print("5. High Humidity Test Passed!")

    # 6. Combined Risk Factors & Bounded 0-100 check
    b6 = Batch(id=106, batch_code="B6-CRITICAL", harvest_date=today - timedelta(days=20), expiry_date=today - timedelta(days=2), product=p)
    inv6 = Inventory(id=206, batch_id=106, batch=b6, temperature=30.0, humidity=90.0, warehouse_location="Test Hub", quantity=100.0)
    res6 = evaluate_inventory_spoilage_risk(inv6)
    assert 0 <= res6["risk_score"] <= 100
    assert res6["risk_score"] == 100  # Capped at 100
    assert res6["risk_level"] == "High"
    assert "Prioritize immediate dispatch" in res6["recommendation"]
    assert len(res6["factors"]) >= 3
    print("6. Combined Risk & Bounded Score Test Passed!")


def test_spoilage_api_endpoints():
    print("\n--- Testing GET /api/v1/spoilage/risk ---")
    login_resp = client.post("/api/auth/login", json={"email": "admin@agroflow.com", "password": "Admin@AgroFlow2026!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r1 = client.get("/api/spoilage/risk", headers=headers)
    assert r1.status_code == 200
    data1 = r1.json()
    assert isinstance(data1, list)
    if len(data1) > 0:
        item = data1[0]
        assert "risk_score" in item
        assert "risk_level" in item
        assert "factors" in item
        assert "recommendation" in item
        assert 0 <= item["risk_score"] <= 100
    print("GET /api/spoilage/risk Passed! Evaluated", len(data1), "inventory lots.")

    print("\n--- Testing GET /api/spoilage/summary ---")
    r2 = client.get("/api/spoilage/summary", headers=headers)
    assert r2.status_code == 200
    summary = r2.json()
    assert "total_analyzed" in summary
    assert "low_risk_count" in summary
    assert "medium_risk_count" in summary
    assert "high_risk_count" in summary
    assert "average_risk_score" in summary
    assert "highest_risk_batches" in summary
    assert "disclaimer" in summary
    print("GET /api/v1/spoilage/summary Passed! Total analyzed:", summary["total_analyzed"])


if __name__ == "__main__":
    test_spoilage_scoring_unit_cases()
    test_spoilage_api_endpoints()
    print("\n==========================================")
    print("ALL SPOILAGE INTELLIGENCE TESTS PASSED 100%")
    print("==========================================")
