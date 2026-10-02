import os
import sys
from dotenv import load_dotenv

# Ensure backend directory is in sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.database import SessionLocal, engine, Base
import app.models
from app.models.user import User, UserRole
from app.services.auth_service import get_password_hash

load_dotenv()

def initialize_admin_account():
    print("=" * 60)
    print("AGROFLOW AI — PRIVILEGED ADMIN ACCOUNT INITIALIZATION")
    print("=" * 60)

    Base.metadata.create_all(bind=engine)

    admin_name = os.getenv("ADMIN_NAME", "AgroFlow Administrator")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@agroflow.com").strip().lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if existing_admin:
            print(f"[INFO] Admin user '{admin_email}' already exists in PostgreSQL database (ID: {existing_admin.id}).")
            existing_admin.password_hash = get_password_hash(admin_password)
            if existing_admin.role != UserRole.ADMIN.value:
                existing_admin.role = UserRole.ADMIN.value
            db.commit()
            print(f"[SUCCESS] Updated password hash and role for admin user '{admin_email}'.")
            return

        hashed_pwd = get_password_hash(admin_password)
        admin_user = User(
            name=admin_name,
            email=admin_email,
            password_hash=hashed_pwd,
            role=UserRole.ADMIN.value
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print(f"[SUCCESS] Privileged Admin account successfully created!")
        print(f"  Name:  {admin_user.name}")
        print(f"  Email: {admin_user.email}")
        print(f"  Role:  {admin_user.role}")
        print("  Password initialized securely from environment configuration.")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to initialize admin account: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    initialize_admin_account()
