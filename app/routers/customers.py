"""
Customer router

Minimal CRUD needed so Payment/Subscription (both have a required
customer_id foreign key) have a real customer to point at.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from loguru import logger

from app.database import get_db
from app.models.customer import Customer
from app.models.tenant_base import apply_tenant_context
from app.utils.serializers import model_to_dict

router = APIRouter()


class CreateCustomerRequest(BaseModel):
    """Request to create a customer"""
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None


@router.post("/")
async def create_customer(
    request: CreateCustomerRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a customer"""
    try:
        logger.info(f"Creating customer: {request.email}")

        existing = await db.execute(select(Customer).where(Customer.email == request.email))
        if existing.scalar_one_or_none() is not None:
            raise HTTPException(status_code=400, detail=f"Customer already exists: {request.email}")

        customer = Customer(
            email=request.email,
            name=request.name,
            phone=request.phone,
            country=request.country,
        )
        apply_tenant_context(customer)
        db.add(customer)
        await db.commit()
        await db.refresh(customer)

        logger.info(f"Customer created: {customer.id}")
        return model_to_dict(customer)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{customer_id}")
async def get_customer(customer_id: str, db: AsyncSession = Depends(get_db)):
    """Get customer details"""
    try:
        customer = await db.get(Customer, uuid.UUID(customer_id))
        if customer is None:
            raise HTTPException(status_code=404, detail=f"Customer not found: {customer_id}")

        return model_to_dict(customer)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))
