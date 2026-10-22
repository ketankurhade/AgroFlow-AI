import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_duplicate_storage_intake_workflow():
    suffix = str(uuid.uuid4())[:8]

    # Register farmer/manager users
    r_farmer = client.post("/api/auth/register", json={
        "name": "Storage Farmer", "email": f"farmer.storage.{suffix}@agroflow.com", "password": "FarmerPassword123!", "role": "farmer"
    })
    assert r_farmer.status_code == 201, f"Farmer registration failed: {r_farmer.text}"
    farmer_id = r_farmer.json()["id"]
    t_farmer = client.post("/api/auth/login", json={"email": f"farmer.storage.{suffix}@agroflow.com", "password": "FarmerPassword123!"}).json()["access_token"]
    h_farmer = {"Authorization": f"Bearer {t_farmer}"}

    r_mgr = client.post("/api/auth/register", json={
        "name": "Storage Manager", "email": f"mgr.storage.{suffix}@agroflow.com", "password": "ManagerPassword123!", "role": "supply_chain_manager"
    })
    assert r_mgr.status_code == 201, f"Manager registration failed: {r_mgr.text}"
    t_mgr = client.post("/api/auth/login", json={"email": f"mgr.storage.{suffix}@agroflow.com", "password": "ManagerPassword123!"}).json()["access_token"]
    h_mgr = {"Authorization": f"Bearer {t_mgr}"}

    # 1. Create a new harvest batch as farmer
    batch_payload = {
        "batch_code": f"BATCH-STOR-{suffix}",
        "product_id": 1, # Onion
        "farmer_id": farmer_id,
        "quantity": 500.0,
        "quality_grade": "Grade A",
        "harvest_date": "2026-10-01",
        "expiry_date": "2026-11-01",
        "origin_location": "Nashik Farm",
        "status": "Harvested"
    }
    r_batch = client.post("/api/batches", headers=h_farmer, json=batch_payload)
    assert r_batch.status_code == 201, f"Failed to create batch: {r_batch.text}"
    batch_id = r_batch.json()["id"]

    # TEST 1: Unintaked batch MUST appear in GET /api/batches?unintaked_only=true
    r_unintaked_before = client.get("/api/batches?unintaked_only=true", headers=h_mgr)
    assert r_unintaked_before.status_code == 200
    unintaked_ids = [b["id"] for b in r_unintaked_before.json()]
    assert batch_id in unintaked_ids, "Newly created harvest batch must appear in unintaked_only batches API"

    # TEST 2: Perform storage intake (POST /api/inventory) for the first time
    storage_intake_payload = {
        "batch_id": batch_id,
        "warehouse_location": "Mumbai Central Storage - Bay A",
        "quantity": 500.0,
        "temperature": 18.0,
        "humidity": 65.0
    }
    r_intake = client.post("/api/inventory", headers=h_mgr, json=storage_intake_payload)
    assert r_intake.status_code == 201, f"Initial storage intake failed: {r_intake.text}"

    # TEST 3: Intaked batch MUST NO LONGER appear in GET /api/batches?unintaked_only=true
    r_unintaked_after = client.get("/api/batches?unintaked_only=true", headers=h_mgr)
    assert r_unintaked_after.status_code == 200
    unintaked_ids_after = [b["id"] for b in r_unintaked_after.json()]
    assert batch_id not in unintaked_ids_after, "Intaked batch must NOT appear in unintaked_only batches API"

    # TEST 4: Direct duplicate storage intake MUST be rejected with HTTP 400
    r_intake_dup = client.post("/api/inventory", headers=h_mgr, json=storage_intake_payload)
    assert r_intake_dup.status_code == 400, f"Expected 400 Bad Request, got {r_intake_dup.status_code}: {r_intake_dup.text}"
    assert "already has active storage inventory" in r_intake_dup.json()["detail"]

    # TEST 5: Check QR traceability timeline has exactly 1 Cold Storage Intake event
    r_trace = client.get(f"/api/traceability/batch/{batch_id}", headers=h_mgr)
    assert r_trace.status_code == 200
    events = r_trace.json()
    intake_events = [e for e in events if e["stage"] == "Cold Storage Intake"]
    assert len(intake_events) == 1, f"Expected exactly 1 Cold Storage Intake event, got {len(intake_events)}"

    print("[ALL DUPLICATE STORAGE INTAKE TESTS PASSED]")
