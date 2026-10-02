import os
import sys
import uuid
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)


def test_farmer_risk_ownership_matrix():
    print("=" * 80)
    print("AGROFLOW AI — FARMER RISK MANAGEMENT OWNERSHIP & VISIBILITY TEST SUITE")
    print("=" * 80)

    unique_id = str(uuid.uuid4())[:8]

    # 1. AUTHENTICATE ADMIN & GET GLOBAL INITIAL RISK PICTURE
    print("\n--- Step 1: Admin Authentication & Global Initial Risk Check ---")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@agroflow.com")
    admin_pwd = os.getenv("ADMIN_PASSWORD", "Admin@AgroFlow2026!")
    r_admin_login = client.post("/api/auth/login", json={"email": admin_email, "password": admin_pwd})
    assert r_admin_login.status_code == 200, f"Admin login failed: {r_admin_login.text}"
    admin_token = r_admin_login.json()["access_token"]
    admin_h = {"Authorization": f"Bearer {admin_token}"}

    r_admin_summary = client.get("/api/spoilage/summary", headers=admin_h)
    assert r_admin_summary.status_code == 200
    admin_summary = r_admin_summary.json()
    print(f"  [OK] Admin sees global spoilage risk summary (Total Analyzed: {admin_summary['total_analyzed']}, High Risk: {admin_summary['high_risk_count']}).")

    # 2. REGISTER & VERIFY BRAND-NEW FARMER A (0 BATCHES/INVENTORY)
    print("\n--- Step 2: Register & Verify Brand-New Farmer A (0 Batches/Inventory/Risk) ---")
    farmer_a_email = f"farmer.a.risk.{unique_id}@agroflow.com"
    pwd = "Password123!farmer"
    r_reg_a = client.post("/api/auth/register", json={
        "name": "Farmer Alice Risk",
        "email": farmer_a_email,
        "password": pwd,
        "role": "farmer"
    })
    assert r_reg_a.status_code == 201
    r_login_a = client.post("/api/auth/login", json={"email": farmer_a_email, "password": pwd})
    assert r_login_a.status_code == 200
    token_a = r_login_a.json()["access_token"]
    farmer_a_id = r_login_a.json()["user"]["id"]
    h_farmer_a = {"Authorization": f"Bearer {token_a}"}

    # Farmer A GET /api/spoilage/risk
    r_risk_a = client.get("/api/spoilage/risk", headers=h_farmer_a)
    assert r_risk_a.status_code == 200
    risk_a = r_risk_a.json()
    assert len(risk_a) == 0, f"Brand new Farmer A should see 0 risk records, got {len(risk_a)}"
    print("  [OK] Farmer A GET /api/spoilage/risk returned empty array [].")

    # Farmer A GET /api/spoilage/summary
    r_summary_a = client.get("/api/spoilage/summary", headers=h_farmer_a)
    assert r_summary_a.status_code == 200
    summary_a = r_summary_a.json()
    assert summary_a["total_analyzed"] == 0, f"Farmer A total_analyzed should be 0, got {summary_a['total_analyzed']}"
    assert summary_a["high_risk_count"] == 0, f"Farmer A high_risk_count should be 0, got {summary_a['high_risk_count']}"
    assert summary_a["medium_risk_count"] == 0
    assert summary_a["low_risk_count"] == 0
    print("  [OK] Farmer A GET /api/spoilage/summary returned zero counts (Total: 0, High Risk: 0).")

    # 3. REGISTER FARMER B, CREATE BATCH & INVENTORY WITH HIGH RISK
    print("\n--- Step 3: Register Farmer B & Create Risky Inventory ---")
    farmer_b_email = f"farmer.b.risk.{unique_id}@agroflow.com"
    r_reg_b = client.post("/api/auth/register", json={
        "name": "Farmer Bob Risk",
        "email": farmer_b_email,
        "password": pwd,
        "role": "farmer"
    })
    assert r_reg_b.status_code == 201
    r_login_b = client.post("/api/auth/login", json={"email": farmer_b_email, "password": pwd})
    assert r_login_b.status_code == 200
    token_b = r_login_b.json()["access_token"]
    farmer_b_id = r_login_b.json()["user"]["id"]
    h_farmer_b = {"Authorization": f"Bearer {token_b}"}

    # Create batch owned by Farmer B
    r_batch_b = client.post("/api/batches", json={
        "batch_code": f"BATCH-RISK-B-{unique_id}",
        "product_id": 1,
        "farmer_id": farmer_b_id,
        "quantity": 300.0,
        "quality_grade": "Grade B",
        "harvest_date": "2026-09-20",
        "expiry_date": "2026-09-30",
        "origin_location": "Nashik Risk Farm",
        "status": "Harvested"
    }, headers=h_farmer_b)
    assert r_batch_b.status_code == 201
    batch_b_id = r_batch_b.json()["id"]

    # Create inventory for Farmer B's batch with elevated temp & humidity (creating measurable risk)
    r_inv_b = client.post("/api/inventory", json={
        "batch_id": batch_b_id,
        "warehouse_location": "Nashik Cold Storage Hub - Section B",
        "quantity": 300.0,
        "temperature": 29.5, # elevated temp
        "humidity": 82.0 # high humidity
    }, headers=admin_h) # Admin or Warehouse creates inventory for the batch
    assert r_inv_b.status_code == 201
    inventory_b_id = r_inv_b.json()["id"]
    print(f"  [OK] Created Batch ID {batch_b_id} (Farmer B) and Inventory ID {inventory_b_id} with elevated ambient temperature/humidity.")

    # 4. VERIFY FARMER B CAN SEE THEIR OWN INVENTORY RISK
    print("\n--- Step 4: Verify Farmer B Risk Visibility ---")
    r_risk_b = client.get("/api/spoilage/risk", headers=h_farmer_b)
    assert r_risk_b.status_code == 200
    risk_b = r_risk_b.json()
    assert len(risk_b) >= 1, f"Farmer B should see inventory risk items, got {len(risk_b)}"
    matching_risk = [r for r in risk_b if r["inventory_id"] == inventory_b_id]
    assert len(matching_risk) == 1, f"Expected 1 risk record for created inventory {inventory_b_id}"
    assert matching_risk[0]["batch_id"] == batch_b_id
    print(f"  [OK] Farmer B sees their own inventory risk (Risk Score: {matching_risk[0]['risk_score']}, Level: {matching_risk[0]['risk_level']}).")

    r_summary_b = client.get("/api/spoilage/summary", headers=h_farmer_b)
    assert r_summary_b.status_code == 200
    summary_b = r_summary_b.json()
    assert summary_b["total_analyzed"] >= 1
    assert summary_b["high_risk_count"] >= 1
    print(f"  [OK] Farmer B summary shows {summary_b['total_analyzed']} total analyzed items and {summary_b['high_risk_count']} high risk batch.")

    # 5. VERIFY CROSS-FARMER ISOLATION (FARMER A CANNOT SEE FARMER B'S RISK)
    print("\n--- Step 5: Verify Cross-Farmer Risk Isolation (Farmer A vs Farmer B) ---")
    r_risk_a_post = client.get("/api/spoilage/risk", headers=h_farmer_a)
    assert r_risk_a_post.status_code == 200
    assert len(r_risk_a_post.json()) == 0, "Farmer A must still see 0 risk records."

    r_summary_a_post = client.get("/api/spoilage/summary", headers=h_farmer_a)
    assert r_summary_a_post.status_code == 200
    assert r_summary_a_post.json()["total_analyzed"] == 0, "Farmer A summary must still show 0 analyzed."
    print("  [OK] Farmer A strictly receives 0 risk records and 0 summary counts.")

    # 6. UNAUTHORIZED BATCH / INVENTORY QUERY ATTEMPTS
    print("\n--- Step 6: Unauthorized Specific Batch / Inventory Risk Queries ---")
    r_tamper_batch = client.get(f"/api/spoilage/risk?batch_id={batch_b_id}", headers=h_farmer_a)
    assert r_tamper_batch.status_code == 403, f"Farmer A requesting Farmer B's batch_id risk should return 403, got {r_tamper_batch.status_code}"
    print("  [OK] GET /api/spoilage/risk?batch_id={Farmer_B_Batch} for Farmer A strictly rejected with HTTP 403 Forbidden.")

    r_tamper_inv = client.get(f"/api/spoilage/risk?inventory_id={inventory_b_id}", headers=h_farmer_a)
    assert r_tamper_inv.status_code == 403, f"Farmer A requesting Farmer B's inventory_id risk should return 403, got {r_tamper_inv.status_code}"
    print("  [OK] GET /api/spoilage/risk?inventory_id={Farmer_B_Inventory} for Farmer A strictly rejected with HTTP 403 Forbidden.")

    # 7. ML SPOILAGE PREDICTION OWNERSHIP ENFORCEMENT
    print("\n--- Step 7: ML Spoilage Prediction Ownership Enforcement ---")
    ml_payload_tamper = {
        "batch_id": batch_b_id,
        "product_name": "Mango",
        "category": "Fruits",
        "day_of_week": 2,
        "month": 6,
        "season": "Summer",
        "temperature": 28.5,
        "humidity": 78.0,
        "inventory_age_days": 10,
        "remaining_shelf_life_days": 2,
        "inventory_quantity_kg": 1200.0,
        "historical_demand_kg": 1000.0,
        "supply_quantity_kg": 1100.0
    }
    r_ml_tamper = client.post("/api/spoilage/ml-predict", json=ml_payload_tamper, headers=h_farmer_a)
    assert r_ml_tamper.status_code == 403, f"Farmer A ML prediction for Farmer B's batch_id should return 403, got {r_ml_tamper.status_code}"
    print("  [OK] POST /api/spoilage/ml-predict for another farmer's batch_id strictly rejected with HTTP 403 Forbidden.")

    r_analyze_tamper = client.post("/api/spoilage/analyze", json=ml_payload_tamper, headers=h_farmer_a)
    assert r_analyze_tamper.status_code == 403, f"Farmer A combined analysis for Farmer B's batch_id should return 403, got {r_analyze_tamper.status_code}"
    print("  [OK] POST /api/spoilage/analyze for another farmer's batch_id strictly rejected with HTTP 403 Forbidden.")

    # 8. ADMIN UNFILTERED RISK ACCESS
    print("\n--- Step 8: Verify Admin Global Risk Visibility ---")
    r_admin_final = client.get("/api/spoilage/summary", headers=admin_h)
    assert r_admin_final.status_code == 200
    admin_summary_final = r_admin_final.json()
    assert admin_summary_final["total_analyzed"] == admin_summary["total_analyzed"] + 1
    print(f"  [OK] Admin global risk summary includes newly created inventory (Total Analyzed: {admin_summary_final['total_analyzed']}).")

    print("\n" + "=" * 80)
    print("ALL FARMER RISK OWNERSHIP & VISIBILITY TESTS PASSED 100%!")
    print("=" * 80)


if __name__ == "__main__":
    test_farmer_risk_ownership_matrix()
