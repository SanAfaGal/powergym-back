from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from app.schemas.subscription import Subscription, SubscriptionCreate, SubscriptionRenew, SubscriptionCancel
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.plan_repository import PlanRepository
from app.db.models import SubscriptionStatusEnum, SubscriptionModel, ClientModel
from app.utils.subscription.calculator import SubscriptionCalculator
from app.utils.common.formatters import format_client_name
from app.services.notification_service import NotificationService
from app.core.async_processing import run_async_in_background
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Business logic for subscriptions"""

    @staticmethod
    def create_subscription(db: Session, subscription_data: SubscriptionCreate) -> Subscription:
        """Create a new subscription"""
        from decimal import Decimal
        
        plan = PlanRepository.get_by_id(db, subscription_data.plan_id)
        if not plan:
            raise ValueError(f"Plan {subscription_data.plan_id} not found")
        
        end_date = SubscriptionCalculator.calculate_end_date(subscription_data.start_date, plan)

        # Calculate final price if discount is provided
        final_price = None
        meta_info = {}
        if subscription_data.discount_percentage is not None:
            original_price = float(plan.price)
            discount_percentage = subscription_data.discount_percentage
            final_price = original_price * (1 - discount_percentage / 100)
            
            # Store pricing info in meta_info for audit trail
            meta_info = {
                "original_price": original_price,
                "discount_percentage": discount_percentage,
                "final_price": final_price,
                "discount_amount": original_price - final_price
            }

        subscription_model = SubscriptionRepository.create(
            db=db,
            client_id=subscription_data.client_id,
            plan_id=subscription_data.plan_id,
            start_date=subscription_data.start_date,
            end_date=end_date,
            status=SubscriptionStatusEnum.PENDING_PAYMENT,
            final_price=final_price
        )
        
        # Update meta_info if discount was applied
        if meta_info:
            current_meta = subscription_model.meta_info or {}
            subscription_model.meta_info = {**current_meta, **meta_info}
            db.commit()
            db.refresh(subscription_model)

        # Send Telegram notification in background
        try:
            # Reload subscription with relationships
            subscription_with_rels = db.query(SubscriptionModel).options(
                joinedload(SubscriptionModel.client),
                joinedload(SubscriptionModel.plan)
            ).filter(SubscriptionModel.id == subscription_model.id).first()

            if subscription_with_rels and subscription_with_rels.client and subscription_with_rels.plan:
                # Format client name using utility function
                client_name = format_client_name(
                    first_name=subscription_with_rels.client.first_name,
                    last_name=subscription_with_rels.client.last_name,
                    middle_name=subscription_with_rels.client.middle_name,
                    second_last_name=subscription_with_rels.client.second_last_name
                )

                # Send notification asynchronously (fire and forget)
                run_async_in_background(
                    NotificationService.send_subscription_notification(
                        client_name=client_name,
                        plan_name=subscription_with_rels.plan.name,
                        start_date=subscription_data.start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d"),
                        plan_price=float(plan.price),
                        status=subscription_model.status.value
                    )
                )
        except Exception as e:
            # Log error but don't fail the subscription creation
            logger.error("Error sending subscription notification: %s", str(e), exc_info=True)

        return Subscription.from_orm(subscription_model)

    @staticmethod
    def get_active_subscription_by_client(db: Session, client_id: UUID) -> Optional[Subscription]:
        """Get the active subscription for a client (only one can exist)"""
        subscriptions = SubscriptionRepository.get_active_by_client(db, client_id)
        if subscriptions:
            return Subscription.from_orm(subscriptions[0])
        return None

    @staticmethod
    def get_subscriptions_by_client(
            db: Session,
            client_id: UUID,
            limit: int = 100,
            offset: int = 0
    ) -> List[Subscription]:
        """Get all subscriptions for a client"""
        subscription_models = SubscriptionRepository.get_by_client(db, client_id, limit, offset)
        return [Subscription.from_orm(sub) for sub in subscription_models]

    @staticmethod
    def renew_subscription(
            db: Session,
            renewal_data: SubscriptionRenew
    ) -> Subscription:
        """
        Renew a subscription.

        Logic:
        - Takes the current subscription's end_date and adds 1 day as start_date
        - Uses provided plan_id, or same plan if not specified
        - New subscription always starts as PENDING_PAYMENT
        """
        from datetime import timedelta
        from decimal import Decimal

        old_sub = SubscriptionRepository.get_by_id(db, renewal_data.subscription_id)
        if not old_sub:
            raise ValueError(f"Subscription {renewal_data.subscription_id} not found")

        # Use provided plan or keep the same plan
        plan_id = renewal_data.plan_id or old_sub.plan_id
        plan = PlanRepository.get_by_id(db, plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        # Renewal always starts the day after current subscription ends
        renewal_start = old_sub.end_date + timedelta(days=1)
        end_date = SubscriptionCalculator.calculate_end_date(renewal_start, plan)

        # Calculate final price if discount is provided
        final_price = None
        meta_info = {}
        if renewal_data.discount_percentage is not None:
            original_price = float(plan.price)
            discount_percentage = renewal_data.discount_percentage
            final_price = original_price * (1 - discount_percentage / 100)
            
            # Store pricing info in meta_info for audit trail
            meta_info = {
                "original_price": original_price,
                "discount_percentage": discount_percentage,
                "final_price": final_price,
                "discount_amount": original_price - final_price
            }

        subscription_model = SubscriptionRepository.create(
            db=db,
            client_id=renewal_data.client_id,
            plan_id=plan_id,
            start_date=renewal_start,
            end_date=end_date,
            status=SubscriptionStatusEnum.PENDING_PAYMENT,
            final_price=final_price
        )
        
        # Update meta_info if discount was applied
        if meta_info:
            current_meta = subscription_model.meta_info or {}
            subscription_model.meta_info = {**current_meta, **meta_info}
            db.commit()
            db.refresh(subscription_model)

        return Subscription.from_orm(subscription_model)

    @staticmethod
    def cancel_subscription(
            db: Session,
            cancel_data: SubscriptionCancel
    ) -> Subscription:
        """Cancel a subscription"""
        subscription_model = SubscriptionRepository.cancel(
            db=db,
            subscription_id=cancel_data.subscription_id,
            cancellation_reason=cancel_data.cancellation_reason
        )

        return Subscription.from_orm(subscription_model)
