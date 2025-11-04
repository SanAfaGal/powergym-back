from pydantic import BaseModel, Field
from enum import Enum
from datetime import date, datetime
from uuid import UUID
from typing import Optional


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING_PAYMENT = "pending_payment"
    CANCELED = "canceled"
    SCHEDULED = "scheduled"


# ============= INPUT SCHEMAS =============

class SubscriptionCreateInput(BaseModel):
    """Input to create a subscription"""
    plan_id: UUID = Field(..., description="Plan ID")
    start_date: date = Field(..., description="Subscription start date")
    discount_percentage: Optional[float] = Field(
        None,
        ge=0.01,
        le=100.0,
        description="Optional discount percentage (0.01 to 100.0)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "plan_id": "123e4567-e89b-12d3-a456-426614174001",
                "start_date": "2025-01-01",
                "discount_percentage": 20.0
            }]
        }
    }


class SubscriptionRenewInput(BaseModel):
    """Input to renew a subscription"""
    plan_id: Optional[UUID] = Field(
        default=None,
        description="Plan ID for renewal (defaults to same plan if not provided)"
    )
    discount_percentage: Optional[float] = Field(
        None,
        ge=0.01,
        le=100.0,
        description="Optional discount percentage (0.01 to 100.0)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "plan_id": None,
                    "discount_percentage": 20.0
                },
                {
                    "plan_id": "123e4567-e89b-12d3-a456-426614174001",
                    "discount_percentage": None
                }
            ]
        }
    }


class SubscriptionCancelInput(BaseModel):
    """Input to cancel a subscription"""
    cancellation_reason: Optional[str] = Field(
        default=None,
        description="Reason for cancellation"
    )


# ============= INTERNAL SCHEMAS =============

class SubscriptionCreate(BaseModel):
    """Internal schema with client_id injected"""
    client_id: UUID
    plan_id: UUID
    start_date: date
    discount_percentage: Optional[float] = None


class SubscriptionRenew(BaseModel):
    """Internal schema for renewal"""
    client_id: UUID
    subscription_id: UUID
    plan_id: Optional[UUID] = None
    discount_percentage: Optional[float] = None


class SubscriptionCancel(BaseModel):
    """Internal schema for cancellation"""
    subscription_id: UUID
    cancellation_reason: Optional[str] = None


# ============= OUTPUT SCHEMAS =============

class Subscription(BaseModel):
    """Subscription response"""
    id: UUID
    client_id: UUID
    plan_id: UUID
    start_date: date
    end_date: date
    status: SubscriptionStatus
    cancellation_date: Optional[date] = None
    cancellation_reason: Optional[str] = None
    final_price: Optional[float] = Field(
        None,
        description="Final price with discount applied (if any). If None, uses plan.price"
    )
    created_at: datetime
    updated_at: datetime
    meta_info: Optional[dict] = None

    class Config:
        from_attributes = True
