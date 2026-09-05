"""
Revenue Operations Engine - Main Application
Financial backbone for the Autonomous Company OS
"""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from loguru import logger
import os

from unkey_auth import require_api_key

from app.config import settings
from app.database import init_db
from app.routers import payments, subscriptions, invoices, analytics, dunning, webhooks, customers
from app.middleware.tenant import TenantMiddleware
from empire_operators.middleware import SafetyBoundaryMiddleware


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
    lifespan=lifespan,
    # SECURITY_REVIEW.md finding: /docs, /redoc, /openapi.json were reachable
    # unauthenticated on every engine (dynamic-pentest-confirmed) - a full
    # interactive API browser plus every unauth write path. Disabled unless
    # DEBUG=true.
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

# Configure CORS
def _cors_allowed_origins() -> list:
    # SECURITY_REVIEW.md #1 - no wildcard with credentials. Set
    # ALLOWED_ORIGINS (comma-separated) when a browser client exists.
    import os
    return [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add tenant middleware for multi-tenancy support
app.add_middleware(TenantMiddleware)

# Reject request bodies matching known-unsafe patterns (prompt injection,
# `drop table`, `<script>`) before they reach a router. empire_os
# SafetyBoundaryOperator via the empire-operators sibling — Step 8 Phase B
# rollout, see EMPIRE_OS_INTEGRATION_ANALYSIS.md + SECURITY_REVIEW.md.
# Note: also scans the unauthenticated /webhooks bodies (Stripe event
# JSON) — the unsafe patterns don't occur in legitimate webhook payloads.
app.add_middleware(SafetyBoundaryMiddleware)

# Include routers - gated by Unkey key verification (fails open until
# UNKEY_ROOT_KEY is configured; see unkey-auth/README.md). webhooks is
# deliberately excluded: inbound calls from Stripe/PayPal are verified by
# provider signature, not our own API keys.
_auth = [Depends(require_api_key)]
app.include_router(customers.router, prefix="/customers", tags=["customers"], dependencies=_auth)
app.include_router(payments.router, prefix="/payments", tags=["payments"], dependencies=_auth)
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"], dependencies=_auth)
app.include_router(invoices.router, prefix="/invoices", tags=["invoices"], dependencies=_auth)
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"], dependencies=_auth)
app.include_router(dunning.router, prefix="/dunning", tags=["dunning"], dependencies=_auth)
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
            "customers": "/customers",
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
    logger.info("Health check performed")
    return {
        "status": "healthy",
        "service": "revenue-operations-engine",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8036,
        reload=True
    )
