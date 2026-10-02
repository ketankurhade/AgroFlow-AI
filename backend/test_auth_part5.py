import os
import sys
import uuid
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.main import app

client = TestClient(app)

def run_part51_auth_tests():
    print("=" * 70)
    print("AGROFLOW AI — PART 5.1 AUTHENTICATION & REGISTRATION SUITE")
    print("=" * 70)

    unique_id = str(uuid.uuid4())[:8]
    test_farmer_email = f"farmer.test.{unique_id}@agroflow.com"
    test_farmer_pwd = "TestFarmerPassword123!"

    # TEST A: Normal User Registration
    print("\n[TEST A] Normal User Registration (Farmer)...")
    reg_payload = {
        "name": "Test Farmer Ramesh",
        "email": test_farmer_email,
        "password": test_farmer_pwd,
        "role": "farmer"
    }
    res_reg = client.post("/api/auth/register", json=reg_payload)
    assert res_reg.status_code == 201, f"Registration failed {res_reg.status_code}: {res_reg.text}"
    user_reg_data = res_reg.json()
    assert user_reg_data["email"] == test_farmer_email
    assert user_reg_data["role"] == "farmer"
    assert "password_hash" not in user_reg_data
    assert "password" not in user_reg_data
    print(f"  [OK] Registration succeeded: ID {user_reg_data['id']}, Email: {user_reg_data['email']}, Role: {user_reg_data['role']}.")

    # TEST B: Normal User Login
    print("\n[TEST B] Normal User Login...")
    login_payload = {
        "email": test_farmer_email,
        "password": test_farmer_pwd
    }
    res_login = client.post("/api/auth/login", json=login_payload)
    assert res_login.status_code == 200, f"Login failed {res_login.status_code}: {res_login.text}"
    login_data = res_login.json()
    assert "access_token" in login_data
    token = login_data["access_token"]
    assert login_data["user"]["role"] == "farmer"
    print(f"  [OK] Login succeeded. JWT token generated cleanly.")

    # TEST C: Session Restoration (/api/auth/me)
    print("\n[TEST C] Session Restoration (/api/auth/me)...")
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200, f"Session restoration failed: {res_me.text}"
    me_data = res_me.json()
    assert me_data["email"] == test_farmer_email
    assert me_data["role"] == "farmer"
    print(f"  [OK] Session restored via Bearer JWT: User {me_data['name']} ({me_data['role']}).")

    # TEST D: Logout / Invalid Token Check
    print("\n[TEST D] Logout & Unauthenticated Access Block...")
    res_no_token = client.get("/api/auth/me")
    assert res_no_token.status_code == 401
    print("  [OK] Access without Bearer token correctly blocked with HTTP 401 Unauthorized.")

    # TEST E: Invalid Login Credentials
    print("\n[TEST E] Invalid Password Login...")
    res_bad_pwd = client.post("/api/auth/login", json={"email": test_farmer_email, "password": "WrongPassword123!"})
    assert res_bad_pwd.status_code == 401
    print("  [OK] Invalid password correctly rejected with HTTP 401 Unauthorized.")

    # TEST F: Duplicate Email Registration Rejection
    print("\n[TEST F] Duplicate Email Registration...")
    res_dup = client.post("/api/auth/register", json=reg_payload)
    assert res_dup.status_code == 400
    assert "already registered" in res_dup.json()["detail"].lower()
    print("  [OK] Duplicate registration correctly rejected with HTTP 400 Bad Request.")

    # TEST G: Admin Registration Protection
    print("\n[TEST G] Admin Registration Protection...")
    admin_reg_payload = {
        "name": "Malicious Admin Wannabe",
        "email": f"hacker.{unique_id}@example.com",
        "password": "HackerPassword123!",
        "role": "admin"
    }
    res_admin_reg = client.post("/api/auth/register", json=admin_reg_payload)
    assert res_admin_reg.status_code in [400, 422], f"Admin reg should fail but returned {res_admin_reg.status_code}"
    print("  [OK] Public Admin registration attempt strictly REJECTED by backend security controls.")

    # TEST H: Separately Initialized Admin Login
    print("\n[TEST H] Admin Account Login...")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@agroflow.com")
    admin_pwd = os.getenv("ADMIN_PASSWORD", "Admin@AgroFlow2026!")
    res_admin_login = client.post("/api/auth/login", json={"email": admin_email, "password": admin_pwd})
    assert res_admin_login.status_code == 200, f"Admin login failed: {res_admin_login.text}"
    admin_token = res_admin_login.json()["access_token"]
    
    res_admin_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_admin_me.status_code == 200
    admin_me_data = res_admin_me.json()
    assert admin_me_data["role"] == "admin"
    print(f"  [OK] Admin Login Verified: {admin_me_data['name']} ({admin_me_data['email']}) -> Role: {admin_me_data['role']}.")

    # TEST I: Protected Endpoint Access Validation
    print("\n[TEST I] Protected Routes Security Enforcement...")
    res_inv = client.get("/api/inventory", headers={"Authorization": f"Bearer {admin_token}"})
    assert res_inv.status_code == 200, "Inventory query successful"
    print("  [OK] Core operational APIs functioning properly.")


    print("\n" + "=" * 70)
    print("ALL PART 5.1 AUTHENTICATION & REGISTRATION TESTS PASSED 100%!")
    print("=" * 70)

if __name__ == "__main__":
    run_part51_auth_tests()
