import sys
import os
from sqlalchemy import text, inspect
from dotenv import load_dotenv

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

load_dotenv(os.path.join(backend_dir, ".env"))

from app.database import engine

REQUIRED_PERMANENT_PRODUCTS = ["Onion", "Potato", "Apple", "Mango"]

def reset_demo_data():
    auto_yes = "--yes" in sys.argv or "-y" in sys.argv

    if not auto_yes:
        print("=" * 60)
        print("AGROFLOW AI — DEMO DATA RESET")
        print("=" * 60)
        print("\nThis will delete:")
        print("  - Batches")
        print("  - Inventory")
        print("  - Orders")
        print("  - Order Items")
        print("  - Shipments")
        print("  - Traceability Events")
        print("\nIt will PRESERVE:")
        print("  - Users")
        print("  - Onion")
        print("  - Potato")
        print("  - Apple")
        print("  - Mango")
        print("  - AI/ML historical data")
        print("\n" + "=" * 60)
        
        try:
            user_input = input("Continue? [yes/no]: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nRESET CANCELLED.")
            sys.exit(0)
            
        if user_input != "yes":
            print("\nRESET CANCELLED.")
            sys.exit(0)

    print("\nExecuting database verification and safety checks...")

    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    # Safety Check 1: Verify users and products tables exist
    if "users" not in existing_tables or "products" not in existing_tables:
        print("RESET ABORTED: Required database tables ('users' or 'products') are missing.")
        sys.exit(1)

    # Safety Check 2: Verify the 4 permanent products exist
    with engine.connect() as conn:
        db_products = conn.execute(text('SELECT name FROM "products"')).scalars().all()
        missing_products = [p for p in REQUIRED_PERMANENT_PRODUCTS if p not in db_products]
        
        if missing_products:
            print(f"RESET ABORTED: One or more permanent AgroFlow products are missing ({', '.join(missing_products)}).")
            sys.exit(1)

    # Deletion order respecting foreign key constraints (EXCLUDING users and products)
    tables_to_clear = [
        "traceability_events",
        "shipments",
        "order_items",
        "orders",
        "inventory",
        "batches"
    ]

    # Safety Check 3: Strictly enforce that users and products are NEVER in tables_to_clear
    assert "users" not in tables_to_clear, "CRITICAL ERROR: 'users' table must never be deleted!"
    assert "products" not in tables_to_clear, "CRITICAL ERROR: 'products' table must never be deleted!"

    print("Beginning transaction cleanup...")
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            for table in tables_to_clear:
                if table in existing_tables:
                    res = conn.execute(text(f'DELETE FROM "{table}"'))
                    print(f"  - Cleared {table}: {res.rowcount} records deleted.")

            # Reset PostgreSQL primary key sequences for cleared tables
            print("\nResetting PostgreSQL sequences for cleared tables...")
            for table in tables_to_clear:
                if table in existing_tables:
                    seq_query = text(f"SELECT pg_get_serial_sequence('{table}', 'id')")
                    seq_name = conn.execute(seq_query).scalar()
                    if seq_name:
                        conn.execute(text(f"ALTER SEQUENCE {seq_name} RESTART WITH 1"))
                        print(f"  - Sequence '{seq_name}' restarted at 1.")

            trans.commit()
            print("\nTransaction committed successfully.")
        except Exception as e:
            trans.rollback()
            print(f"\nRESET FAILED AND ROLLED BACK: {e}")
            sys.exit(1)

    # Final Verification Query
    with engine.connect() as conn:
        user_count = conn.execute(text('SELECT COUNT(*) FROM "users"')).scalar()
        product_count = conn.execute(text('SELECT COUNT(*) FROM "products"')).scalar()
        batch_count = conn.execute(text('SELECT COUNT(*) FROM "batches"')).scalar() if "batches" in existing_tables else 0
        inv_count = conn.execute(text('SELECT COUNT(*) FROM "inventory"')).scalar() if "inventory" in existing_tables else 0
        order_count = conn.execute(text('SELECT COUNT(*) FROM "orders"')).scalar() if "orders" in existing_tables else 0
        item_count = conn.execute(text('SELECT COUNT(*) FROM "order_items"')).scalar() if "order_items" in existing_tables else 0
        shipment_count = conn.execute(text('SELECT COUNT(*) FROM "shipments"')).scalar() if "shipments" in existing_tables else 0
        event_count = conn.execute(text('SELECT COUNT(*) FROM "traceability_events"')).scalar() if "traceability_events" in existing_tables else 0
        ml_count = conn.execute(text('SELECT COUNT(*) FROM "historical_supply_chain_data"')).scalar() if "historical_supply_chain_data" in existing_tables else 0

        prods_in_db = conn.execute(text('SELECT name FROM "products" ORDER BY name')).scalars().all()

    print("\n" + "=" * 60)
    print("RESET COMPLETE")
    print("=" * 60)
    print(f"\nUsers preserved: {user_count}")
    print(f"Products preserved: {product_count}")
    print(f"\nBatches: {batch_count}")
    print(f"Inventory: {inv_count}")
    print(f"Orders: {order_count}")
    print(f"Order Items: {item_count}")
    print(f"Shipments: {shipment_count}")
    print(f"Traceability Events: {event_count}")
    print(f"\nAI/ML historical data: UNTOUCHED ({ml_count} rows)")
    print("\nPermanent products:")
    for p in prods_in_db:
        if p in REQUIRED_PERMANENT_PRODUCTS:
            print(f"  [OK] {p}")
        else:
            print(f"  - {p}")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    reset_demo_data()
