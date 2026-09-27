import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database import engine, Base
import app.models  # Ensures all models are registered with Base.metadata

from app.routers import (
    auth,
    products,
    batches,
    inventory,
    orders,
    shipments,
    traceability,
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
        print("Database tables initialized successfully.")
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


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "AgroFlow AI Backend"
    }
