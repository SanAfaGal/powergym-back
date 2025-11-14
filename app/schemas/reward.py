from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RewardStatus(str, Enum):
    PENDING = "pending"
    APPLIED = "applied"
    EXPIRED = "expired"


# ============= INPUT SCHEMAS =============

class RewardApplyInput(BaseModel):
    """Input to apply a reward"""
    subscription_id: UUID = Field(..., description="Subscription ID where the reward will be applied")
    discount_percentage: float = Field(
        ...,
        ge=0.01,
        le=100.0,
        description="Discount percentage to apply (0.01 to 100.0)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "subscription_id": "123e4567-e89b-12d3-a456-426614174001",
                "discount_percentage": 20.0
            }]
        }
    }


# ============= INTERNAL SCHEMAS =============

class RewardCreate(BaseModel):
    """Internal schema for creating a reward"""
    subscription_id: UUID
    client_id: UUID
    attendance_count: int
    discount_percentage: Decimal = Decimal("20.00")
    eligible_date: date
    expires_at: datetime


# ============= OUTPUT SCHEMAS =============

class Reward(BaseModel):
    """Reward response"""
    id: UUID
    subscription_id: UUID
    client_id: UUID
    attendance_count: int
    discount_percentage: Decimal
    eligible_date: date
    expires_at: datetime
    status: RewardStatus
    applied_at: Optional[datetime] = None
    applied_subscription_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    meta_info: Optional[dict] = None

    class Config:
        from_attributes = True


class RewardEligibilityResponse(BaseModel):
    """Response for reward eligibility calculation"""
    eligible: bool = Field(..., description="Whether the subscription is eligible for a reward")
    attendance_count: int = Field(..., description="Number of attendances in the cycle")
    reward_id: Optional[UUID] = Field(None, description="ID of the created reward (if eligible)")
    expires_at: Optional[datetime] = Field(None, description="Expiration date of the reward (if eligible)")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "eligible": True,
                "attendance_count": 22,
                "reward_id": "123e4567-e89b-12d3-a456-426614174001",
                "expires_at": "2025-11-10T00:00:00Z"
            }]
        }
    }


class RewardConfig(BaseModel):
    """
    Reward system configuration.
    
    Exposes the current reward configuration settings to the frontend.
    This allows the frontend to display accurate reward rules without hardcoding values.
    """
    attendance_threshold: int = Field(
        ...,
        ge=1,
        description="Minimum number of attendances required to qualify for a reward"
    )
    discount_percentage: float = Field(
        ...,
        ge=0.01,
        le=100.0,
        description="Default discount percentage for rewards (0.01 to 100.0)"
    )
    expiration_days: int = Field(
        ...,
        gt=0,
        description="Number of days until a reward expires after becoming eligible"
    )
    eligible_plan_units: List[str] = Field(
        ...,
        description="List of plan duration units eligible for rewards (e.g., ['month', 'week'])"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "attendance_threshold": 20,
                "discount_percentage": 20.0,
                "expiration_days": 7,
                "eligible_plan_units": ["month"]
            }]
        }
    }

