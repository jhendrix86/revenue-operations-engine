"""
Revenue Operations Engine - Main Application
Financial backbone for the Autonomous Company OS
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import os

from app.config import settings
from app.database import init_db
from app.routers import payments, subscriptions, invoices, analytics, dunning, webhooks


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Revenue Operations Engine...")
    
    # Initialize database
    await init_db()
    
    logger.info("Revenue Operations Engine started successfully")
    yield
    
    logger.info("Shutting down Revenue Operations Engine...")


# Create FastAPI application
app = FastAPI(
    title="Revenue Operations Engine",
    description="Financial backbone for the Autonomous Company OS",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(payments.router, prefix="/payments", tags=["payments"])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
app.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(dunning.router, prefix="/dunning", tags=["dunning"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Revenue Operations Engine",
        "version": "1.0.0",
        "status": "operational",
        "description": "Financial backbone for the Autonomous Company OS",
        "endpoints": {
            "payments": "/payments",
            "subscriptions": "/subscriptions",
            "invoices": "/invoices",
            "analytics": "/analytics",
            "dunning": "/dunning",
            "webhooks": "/webhooks"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "revenue-operations-engine",
        "timestamp": logger.info("Health check performed")
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8036,
        reload=True
    )
