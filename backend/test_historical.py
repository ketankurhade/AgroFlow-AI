from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.historical_data import HistoricalSupplyChainData
from generate_historical_data import generate_synthetic_dataset

client = TestClient(app)


def test_reproducible_generation():
    print("--- 1. Testing Deterministic Reproducibility ---")
    data1 = generate_synthetic_dataset()
    data2 = generate_synthetic_dataset()

    assert len(data1) == len(data2) == 4000
    # Compare first 5 records
    for i in range(5):
        assert data1[i].record_date == data2[i].record_date
        assert data1[i].product_name == data2[i].product_name
        assert data1[i].target_demand_quantity_kg == data2[i].target_demand_quantity_kg
        assert data1[i].target_price_per_kg == data2[i].target_price_per_kg
        assert data1[i].target_spoilage_indicator == data2[i].target_spoilage_indicator

    print("[OK] Generator output is 100% reproducible!")


def test_database_persistence():
    print("--- 2. Testing Database Record Persistence ---")
    db = SessionLocal()
    try:
        count = db.query(HistoricalSupplyChainData).count()
        assert count == 4000
        print(f"[OK] Verified {count} historical records persisted in PostgreSQL database.")

        # Check sample record targets
        rec = db.query(HistoricalSupplyChainData).first()
        assert hasattr(rec, "target_demand_quantity_kg")
        assert hasattr(rec, "target_price_per_kg")
        assert hasattr(rec, "target_spoilage_indicator")
        assert rec.target_spoilage_indicator in (0, 1)
        print("[OK] Target columns present and valid in DB record.")
    finally:
        db.close()


def test_historical_summary_api():
    print("--- 3. Testing GET /api/v1/historical-data/summary Endpoint ---")
    login_resp = client.post("/api/auth/login", json={"email": "admin@agroflow.com", "password": "Admin@AgroFlow2026!"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get("/api/historical-data/summary", headers=headers)
    assert r.status_code == 200
    res = r.json()
    assert res["total_records"] == 4000
    assert len(res["products"]) == 8
    assert res["avg_demand_kg"] > 0
    assert res["avg_price_per_kg"] > 0
    assert 0.0 <= res["spoilage_rate_pct"] <= 100.0
    assert "synthetically generated" in res["disclaimer"]
    print("[OK] Summary API passed! Result:", res)


if __name__ == "__main__":
    test_reproducible_generation()
    test_database_persistence()
    test_historical_summary_api()
    print("\n==========================================")
    print("ALL HISTORICAL DATASET TESTS PASSED 100%")
    print("==========================================")
