from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.schemas.subscription import (
    Subscription,
    SubscriptionCreateInput,
    SubscriptionRenewInput,
    SubscriptionCancelInput
)
from app.services.subscription_service import SubscriptionService
from app.api.dependencies import get_current_active_user
from app.schemas.user import User
from app.db.session import get_db
from app.utils.subscription.schema_builder import SubscriptionSchemaBuilder
from app.utils.subscription.validators import SubscriptionValidator
from app.utils.timezone import get_current_colombia_datetime, get_today_colombia

router = APIRouter(prefix="/clients/{client_id}/subscriptions", tags=["subscriptions"])

# Separate router for subscription management endpoints (not tied to a specific client)
subscriptions_router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


class ExpireSubscriptionsResponse(BaseModel):
    """Response schema for subscription expiration endpoint"""
    expired_count: int
    execution_time: str
    reference_date: str


class ActivateSubscriptionsResponse(BaseModel):
    """Response schema for subscription activation endpoint"""
    activated_count: int
    execution_time: str
    reference_date: str


@router.post(
    "/",
    response_model=Subscription,
    status_code=status.HTTP_201_CREATED,
    summary="Create subscription",
    description="Create a new subscription for a client"
)
def create_subscription(
        client_id: UUID,
        subscription_input: SubscriptionCreateInput,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Create a new subscription"""
    # Validations
    SubscriptionValidator.validate_client_exists(db, client_id)
    SubscriptionValidator.validate_client_is_active(db, client_id)

    plan = SubscriptionValidator.validate_plan_exists(db, subscription_input.plan_id)
    SubscriptionValidator.validate_plan_is_active(plan)
    SubscriptionValidator.validate_plan_duration(plan)

    SubscriptionValidator.validate_start_date_not_in_past(subscription_input.start_date)
    SubscriptionValidator.validate_no_active_subscription(db, client_id)

    # Build and create
    subscription_data = SubscriptionSchemaBuilder.build_create(client_id, subscription_input)
    subscription = SubscriptionService.create_subscription(db, subscription_data)

    return subscription


@router.get(
    "/active",
    response_model=Optional[Subscription],
    summary="Get active subscription",
    description="Get the active subscription for a client. Returns null if no active subscription exists."
)
def get_active_subscription(
        client_id: UUID,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Get the active subscription for a client. Returns null if no active subscription exists."""
    SubscriptionValidator.validate_client_exists(db, client_id)

    subscription = SubscriptionService.get_active_subscription_by_client(db, client_id)
    return subscription  # Returns None/null if no active subscription, which is a valid state


@router.get(
    "/",
    response_model=List[Subscription],
    summary="Get client subscriptions",
    description="Get all subscriptions for a client"
)
def get_client_subscriptions(
        client_id: UUID,
        limit: int = 100,
        offset: int = 0,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Get all subscriptions for a client"""
    SubscriptionValidator.validate_client_exists(db, client_id)

    subscriptions = SubscriptionService.get_subscriptions_by_client(db, client_id, limit, offset)
    return subscriptions


@router.post(
    "/{subscription_id}/renew",
    response_model=Subscription,
    status_code=status.HTTP_201_CREATED,
    summary="Renew subscription",
    description="Renew a subscription. Creates a new subscription based on the old one"
)
def renew_subscription(
        client_id: UUID,
        subscription_id: UUID,
        renew_input: SubscriptionRenewInput = None,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Renew a subscription"""
    SubscriptionValidator.validate_client_exists(db, client_id)

    subscription = SubscriptionValidator.validate_subscription_belongs_to_client(
        db, subscription_id, client_id
    )
    SubscriptionValidator.validate_subscription_not_canceled(subscription)

    # Validate no pending renewal already exists
    SubscriptionValidator.validate_no_pending_renewal(db, client_id)

    # Validate plan if provided
    if renew_input and renew_input.plan_id:
        plan = SubscriptionValidator.validate_plan_exists(db, renew_input.plan_id)
        SubscriptionValidator.validate_plan_is_active(plan)
        SubscriptionValidator.validate_plan_duration(plan)

    # Build and renew
    renewal_data = SubscriptionSchemaBuilder.build_renew(
        client_id,
        subscription_id,
        renew_input or SubscriptionRenewInput()
    )
    renewed_subscription = SubscriptionService.renew_subscription(db, renewal_data)

    return renewed_subscription


@router.patch(
    "/{subscription_id}/cancel",
    response_model=Subscription,
    summary="Cancel subscription",
    description="Cancel an active subscription"
)
def cancel_subscription(
        client_id: UUID,
        subscription_id: UUID,
        cancel_input: SubscriptionCancelInput = None,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Cancel a subscription"""
    SubscriptionValidator.validate_client_exists(db, client_id)

    subscription = SubscriptionValidator.validate_subscription_belongs_to_client(
        db, subscription_id, client_id
    )
    SubscriptionValidator.validate_subscription_not_canceled(subscription)

    # Build and cancel
    cancel_data = SubscriptionSchemaBuilder.build_cancel(
        subscription_id,
        cancel_input or SubscriptionCancelInput()
    )
    canceled_subscription = SubscriptionService.cancel_subscription(db, cancel_data)

    return canceled_subscription


@subscriptions_router.post(
    "/expire",
    response_model=ExpireSubscriptionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Expire subscriptions",
    description="Expire all subscriptions that have passed their end_date. Uses America/Bogota timezone for date comparison."
)
def expire_subscriptions(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Expire all subscriptions that have passed their end_date.
    
    This endpoint should be called daily (e.g., via cron) to automatically
    expire subscriptions. Uses the current date in America/Bogota timezone.
    """
    # Execute expiration
    expired_count = SubscriptionService.expire_subscriptions(db)
    
    # Get current time in Colombia timezone
    now_bogota = get_current_colombia_datetime()
    
    return ExpireSubscriptionsResponse(
        expired_count=expired_count,
        execution_time=now_bogota.isoformat(),
        reference_date=now_bogota.date().isoformat()
    )


@subscriptions_router.post(
    "/activate",
    response_model=ActivateSubscriptionsResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate scheduled subscriptions",
    description="Activate all scheduled subscriptions that have reached their start_date. Uses America/Bogota timezone for date comparison."
)
def activate_subscriptions(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Activate all scheduled subscriptions that have reached their start_date.
    
    This endpoint should be called daily (e.g., via cron) to automatically
    activate scheduled subscriptions. Uses the current date in America/Bogota timezone.
    Only activates subscriptions for clients that do not have an active subscription.
    """
    # Execute activation
    activated_count = SubscriptionService.activate_scheduled_subscriptions(db)
    
    # Get current time in Colombia timezone
    now_bogota = get_current_colombia_datetime()
    
    return ActivateSubscriptionsResponse(
        activated_count=activated_count,
        execution_time=now_bogota.isoformat(),
        reference_date=now_bogota.date().isoformat()
    )


# IMPORTANT: This route must be defined BEFORE /{subscription_id} to avoid route conflicts
@subscriptions_router.get(
    "/",
    response_model=List[Subscription],
    summary="Get all subscriptions",
    description="Get all subscriptions across all clients with optional filters"
)
def get_all_subscriptions(
        status: Optional[str] = Query(None, description="Filter by subscription status (active, expired, pending_payment, canceled, scheduled)"),
        client_id: Optional[UUID] = Query(None, description="Filter by specific client ID"),
        limit: int = Query(100, ge=1, le=500, description="Maximum number of results"),
        offset: int = Query(0, ge=0, description="Number of results to skip for pagination"),
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Get all subscriptions with optional filters.
    
    **Parameters:**
    - `status`: Filter by subscription status (active, expired, pending_payment, canceled, scheduled)
    - `client_id`: Filter by specific client ID
    - `limit`: Maximum number of results (default: 100, max: 500)
    - `offset`: Number of results to skip for pagination (default: 0)
    
    **Returns:**
    List of subscriptions with client and plan information included.
    """
    from app.db.models import SubscriptionStatusEnum
    from fastapi import HTTPException
    
    # Parse status if provided
    status_enum = None
    if status:
        try:
            status_enum = SubscriptionStatusEnum(status.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status: {status}. Must be one of: active, expired, pending_payment, canceled, scheduled"
            )
    
    subscriptions = SubscriptionService.get_all_subscriptions(
        db=db,
        limit=limit,
        offset=offset,
        status=status_enum,
        client_id=client_id
    )
    
    return subscriptions


@subscriptions_router.get(
    "/{subscription_id}",
    response_model=Subscription,
    summary="Get subscription by ID",
    description="Get a specific subscription by its ID"
)
def get_subscription_by_id(
        subscription_id: UUID,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Get a subscription by its ID.
    
    **Parameters:**
    - `subscription_id`: Subscription UUID
    
    **Returns:**
    Subscription details with client and plan information included.
    """
    from app.repositories.subscription_repository import SubscriptionRepository
    from app.db.models import SubscriptionModel
    from sqlalchemy.orm import joinedload
    from fastapi import HTTPException
    
    # Get subscription with client and plan relationships
    subscription_model = db.query(SubscriptionModel).options(
        joinedload(SubscriptionModel.client),
        joinedload(SubscriptionModel.plan)
    ).filter(SubscriptionModel.id == subscription_id).first()
    
    if not subscription_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription {subscription_id} not found"
        )
    
    return Subscription.from_orm(subscription_model)