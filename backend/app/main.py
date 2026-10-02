import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import engine, Base, SessionLocal
import app.models  # Ensures all models are registered with Base.metadata
from seed import ensure_products_seeded

from app.routers import (
    auth,
    products,
    batches,
    inventory,
    orders,
    shipments,
    traceability,
    routes,
    spoilage,
    historical,
    demand,
    price,
    intelligence,
)

load_dotenv()

# Allowed origins for CORS
origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if they do not exist
    try:
        Base.metadata.create_all(bind=engine)
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS price FLOAT DEFAULT 45.0;"))
            conn.execute(text("ALTER TABLE inventory ADD COLUMN IF NOT EXISTS owner_id INTEGER REFERENCES users(id);"))
            conn.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS retailer_id INTEGER REFERENCES users(id);"))
            conn.execute(text("ALTER TABLE order_items ADD COLUMN IF NOT EXISTS batch_id INTEGER REFERENCES batches(id);"))
            conn.execute(text("ALTER TABLE shipments ADD COLUMN IF NOT EXISTS expected_delivery_at TIMESTAMP WITH TIME ZONE;"))
            conn.execute(text("ALTER TABLE shipments ADD COLUMN IF NOT EXISTS is_inventory_credited BOOLEAN DEFAULT FALSE;"))
            conn.commit()
        print("Database tables initialized successfully.")
        db = SessionLocal()
        try:
            ensure_products_seeded(db)
        finally:
            db.close()
    except Exception as e:
        print(f"Database initialization warning: {e}")
    yield


app = FastAPI(
    title="AgroFlow AI API",
    description="Backend services for AgroFlow AI agricultural supply chain management",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(batches.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(shipments.router, prefix="/api")
app.include_router(traceability.router, prefix="/api")
app.include_router(routes.router, prefix="/api")
app.include_router(spoilage.router, prefix="/api")
app.include_router(historical.router, prefix="/api")
app.include_router(demand.router, prefix="/api")
app.include_router(price.router, prefix="/api")
app.include_router(intelligence.router, prefix="/api")


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "AgroFlow AI Backend"
    }
