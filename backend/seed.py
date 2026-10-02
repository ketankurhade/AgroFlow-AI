from datetime import date, datetime, timedelta, timezone
from app.database import SessionLocal, engine, Base
import app.models  # Register models
from app.models.user import User, UserRole
from app.models.product import Product
from app.models.batch import Batch
from app.models.inventory import Inventory
from app.models.order import Order, OrderItem
from app.models.shipment import Shipment
from app.models.traceability import TraceabilityEvent
from app.services.auth_service import get_password_hash


DEFAULT_PRODUCTS = [
    {"name": "Onion", "category": "Vegetable", "unit": "kg", "price": 35.0},
    {"name": "Potato", "category": "Vegetable", "unit": "kg", "price": 30.0},
    {"name": "Apple", "category": "Fruit", "unit": "kg", "price": 150.0},
    {"name": "Mango", "category": "Fruit", "unit": "kg", "price": 120.0},
]


def ensure_products_seeded(db):
    """Ensures all default agricultural products are present in the catalog."""
    for prod_def in DEFAULT_PRODUCTS:
        existing = db.query(Product).filter(Product.name == prod_def["name"]).first()
        if not existing:
            db.add(Product(
                name=prod_def["name"],
                category=prod_def["category"],
                unit=prod_def["unit"],
                price=prod_def.get("price", 45.0)
            ))
    db.commit()


def seed_db():
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Ensure default products exist regardless of user presence
        ensure_products_seeded(db)

        # Migrate existing development users with legacy roles to supply_chain_manager
        db.query(User).filter(User.role.in_(["collection_center", "collection_manager", "warehouse", "warehouse_manager"])).update({"role": "supply_chain_manager"}, synchronize_session=False)
        db.commit()

        # Check if users exist to prevent duplicate seeding
        if db.query(User).filter(User.email == "farmer.ramesh@agroflow.com").first():
            print("Seed data already present in database.")
            return

        print("Seeding initial development data...")

        # 1. Farmers, Managers & Buyers
        farmer1 = User(
            name="Ramesh Kumar",
            email="farmer.ramesh@agroflow.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.FARMER.value
        )
        farmer2 = User(
            name="Suresh Patel",
            email="farmer.suresh@agroflow.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.FARMER.value
        )
        manager1 = User(
            name="Anita Sharma",
            email="manager.anita@agroflow.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.SUPPLY_CHAIN_MANAGER.value
        )
        buyer1 = User(
            name="FreshMart Retail",
            email="buyer.freshmart@agroflow.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.RETAILER.value
        )
        buyer2 = User(
            name="Organic Foods Co",
            email="buyer.organic@agroflow.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.DISTRIBUTOR.value
        )

        db.add_all([farmer1, farmer2, manager1, buyer1, buyer2])
        db.flush()

        # Fetch products from DB after ensure_products_seeded
        prod1 = db.query(Product).filter(Product.name == "Organic Alphonso Mangoes").first()
        prod2 = db.query(Product).filter(Product.name == "Fresh Desi Tomatoes").first()

        # 3. Batches
        today = date.today()
        batch1 = Batch(
            batch_code="BATCH-2026-001",
            product_id=prod1.id,
            farmer_id=farmer1.id,
            quantity=500.0,
            quality_grade="Grade A",
            harvest_date=today - timedelta(days=5),
            expiry_date=today + timedelta(days=15),
            origin_location="Nashik Farm, Maharashtra",
            status="In Transit"
        )
        batch2 = Batch(
            batch_code="BATCH-2026-002",
            product_id=prod2.id,
            farmer_id=farmer2.id,
            quantity=1200.0,
            quality_grade="Grade A",
            harvest_date=today - timedelta(days=3),
            expiry_date=today + timedelta(days=10),
            origin_location="Pune Organic Farm, Maharashtra",
            status="Stored"
        )
        batch3 = Batch(
            batch_code="BATCH-2026-003",
            product_id=prod1.id,
            farmer_id=farmer1.id,
            quantity=350.0,
            quality_grade="Grade B",
            harvest_date=today - timedelta(days=2),
            expiry_date=today + timedelta(days=18),
            origin_location="Ratnagiri Orchard, Maharashtra",
            status="Harvested"
        )

        db.add_all([batch1, batch2, batch3])
        db.flush()

        # 4. Inventory Records
        inv1 = Inventory(
            batch_id=batch1.id,
            warehouse_location="Mumbai Cold Storage Facility - Bay 4",
            quantity=500.0,
            temperature=18.5,
            humidity=65.0
        )
        inv2 = Inventory(
            batch_id=batch2.id,
            warehouse_location="Pune Distribution Hub - Section A",
            quantity=1200.0,
            temperature=22.0,
            humidity=70.0
        )
        inv3 = Inventory(
            batch_id=batch3.id,
            warehouse_location="Nagpur Regional Depot - Room 2",
            quantity=350.0,
            temperature=19.0,
            humidity=60.0
        )

        db.add_all([inv1, inv2, inv3])
        db.flush()

        # 5. Orders & OrderItems
        ord1 = Order(
            order_number="ORD-2026-101",
            buyer_id=buyer1.id,
            status="Confirmed",
            total_quantity=200.0,
            total_amount=600.0
        )
        ord2 = Order(
            order_number="ORD-2026-102",
            buyer_id=buyer2.id,
            status="Processing",
            total_quantity=400.0,
            total_amount=1100.0
        )

        db.add_all([ord1, ord2])
        db.flush()

        item1 = OrderItem(order_id=ord1.id, product_id=prod1.id, quantity=200.0, price=3.0)
        item2 = OrderItem(order_id=ord2.id, product_id=prod2.id, quantity=400.0, price=2.75)

        db.add_all([item1, item2])
        db.flush()

        # 6. Shipments
        now = datetime.now(timezone.utc)
        ship1 = Shipment(
            order_id=ord1.id,
            batch_id=batch1.id,
            source="Nashik Cold Storage",
            destination="FreshMart Mumbai Supermarket",
            vehicle_number="MH-15-AB-1234",
            status="In Transit",
            dispatched_at=now - timedelta(hours=4)
        )
        ship2 = Shipment(
            order_id=ord2.id,
            batch_id=batch2.id,
            source="Pune Central Farm",
            destination="Organic Foods Retail Depot",
            vehicle_number="MH-12-CD-5678",
            status="Dispatched",
            dispatched_at=now - timedelta(hours=1)
        )

        db.add_all([ship1, ship2])
        db.flush()

        # 7. Traceability Events
        t1 = TraceabilityEvent(
            batch_id=batch1.id,
            stage="Harvesting",
            location="Nashik Farm, MH",
            description="Batch harvested under optimal moisture conditions.",
            timestamp=now - timedelta(days=5)
        )
        t2 = TraceabilityEvent(
            batch_id=batch1.id,
            stage="Quality Inspection",
            location="Nashik Collection Center",
            description="Passed Grade A certification for sweetness and color.",
            timestamp=now - timedelta(days=4)
        )
        t3 = TraceabilityEvent(
            batch_id=batch1.id,
            stage="Cold Storage Intake",
            location="Mumbai Cold Storage",
            description="Stored at 18.5°C temperature.",
            timestamp=now - timedelta(days=2)
        )
        t4 = TraceabilityEvent(
            batch_id=batch1.id,
            stage="Dispatch",
            location="Mumbai Logistics Hub",
            description="Dispatched via Reefer Truck MH-15-AB-1234.",
            timestamp=now - timedelta(hours=4)
        )

        db.add_all([t1, t2, t3, t4])
        db.commit()

        print("Database seeded successfully with sample data!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
