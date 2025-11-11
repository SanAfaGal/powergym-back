from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from uuid import UUID
from datetime import datetime
from app.schemas.subscription import Subscription, SubscriptionCreate, SubscriptionRenew, SubscriptionCancel
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.plan_repository import PlanRepository
from app.db.models import SubscriptionStatusEnum, SubscriptionModel, ClientModel
from app.utils.subscription.calculator import SubscriptionCalculator
from app.utils.common.formatters import format_client_name
from app.services.notification_service import NotificationService
from app.core.async_processing import run_async_in_background
# TIMEZONE import removed - use specific functions from app.utils.timezone instead
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
    def get_all_subscriptions(
            db: Session,
            limit: int = 100,
            offset: int = 0,
            status: Optional[SubscriptionStatusEnum] = None,
            client_id: Optional[UUID] = None
    ) -> List[Subscription]:
        """Get all subscriptions with optional filters"""
        subscription_models = SubscriptionRepository.get_all(
            db, 
            limit=limit, 
            offset=offset,
            status=status,
            client_id=client_id
        )
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
        - Status is determined by start date:
          * If start_date is in the future: SCHEDULED
          * If start_date is today or in the past: PENDING_PAYMENT
        """
        from datetime import timedelta, date
        from decimal import Decimal
        from app.utils.timezone import get_today_colombia

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

        # Determine status based on start date
        # Get today's date in Colombia timezone
        today_bogota = get_today_colombia()
        
        # If renewal starts in the future, it's SCHEDULED
        # Otherwise, it's PENDING_PAYMENT
        if renewal_start > today_bogota:
            initial_status = SubscriptionStatusEnum.SCHEDULED
        else:
            initial_status = SubscriptionStatusEnum.PENDING_PAYMENT

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
            status=initial_status,
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
                    NotificationService.send_subscription_renew_notification(
                        client_name=client_name,
                        plan_name=subscription_with_rels.plan.name,
                        start_date=renewal_start.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d")
                    )
                )
        except Exception as e:
            # Log error but don't fail the subscription renewal
            logger.error("Error sending subscription renewal notification: %s", str(e), exc_info=True)

        return Subscription.from_orm(subscription_model)

    @staticmethod
    def cancel_subscription(
            db: Session,
            cancel_data: SubscriptionCancel
    ) -> Subscription:
        """
        Cancel a subscription.
        
        If the canceled subscription was ACTIVE and there's a SCHEDULED subscription
        for the same client, update the SCHEDULED subscription status:
        - If start_date <= today: change to PENDING_PAYMENT (can start now)
        - If start_date > today: keep as SCHEDULED (still in the future)
        """
        from datetime import datetime as dt
        from app.utils.timezone import get_today_colombia
        
        # Get the subscription before canceling to check its status and client_id
        subscription_to_cancel = SubscriptionRepository.get_by_id(db, cancel_data.subscription_id)
        if not subscription_to_cancel:
            raise ValueError(f"Subscription {cancel_data.subscription_id} not found")
        
        was_active = subscription_to_cancel.status == SubscriptionStatusEnum.ACTIVE
        client_id = subscription_to_cancel.client_id
        
        # If we're canceling an active subscription, check for scheduled renewals first
        scheduled_to_update = []
        if was_active:
            # Get today's date in Colombia timezone
            today_bogota = get_today_colombia()
            
            # Find SCHEDULED subscriptions for this client
            scheduled_subscriptions = db.query(SubscriptionModel).filter(
                and_(
                    SubscriptionModel.client_id == client_id,
                    SubscriptionModel.status == SubscriptionStatusEnum.SCHEDULED
                )
            ).all()
            
            # Mark SCHEDULED subscriptions that can now start
            for scheduled_sub in scheduled_subscriptions:
                # If the scheduled subscription's start date is today or in the past,
                # change it to PENDING_PAYMENT so it can start
                if scheduled_sub.start_date <= today_bogota:
                    scheduled_sub.status = SubscriptionStatusEnum.PENDING_PAYMENT
                    scheduled_to_update.append(scheduled_sub)
                    logger.info(
                        f"Will update SCHEDULED subscription {scheduled_sub.id} to PENDING_PAYMENT "
                        f"after canceling active subscription {cancel_data.subscription_id}"
                    )
        
        # Cancel the subscription (this will commit)
        subscription_model = SubscriptionRepository.cancel(
            db=db,
            subscription_id=cancel_data.subscription_id,
            cancellation_reason=cancel_data.cancellation_reason
        )
        
        # If we updated scheduled subscriptions, commit those changes
        # (Note: cancel already committed, but we need to commit the scheduled updates)
        if scheduled_to_update:
            try:
                db.commit()
                # Refresh all updated subscriptions
                for scheduled_sub in scheduled_to_update:
                    db.refresh(scheduled_sub)
            except Exception as e:
                db.rollback()
                logger.error(f"Error updating scheduled subscriptions after cancellation: {str(e)}")
                # Don't fail the cancellation if scheduled update fails
                raise

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
                    NotificationService.send_subscription_cancel_notification(
                        client_name=client_name,
                        plan_name=subscription_with_rels.plan.name,
                        cancellation_reason=cancel_data.cancellation_reason
                    )
                )
        except Exception as e:
            # Log error but don't fail the subscription cancellation
            logger.error("Error sending subscription cancellation notification: %s", str(e), exc_info=True)

        return Subscription.from_orm(subscription_model)

    @staticmethod
    def expire_subscriptions(db: Session) -> int:
        """
        Expire all subscriptions that have passed their end_date.

        Uses the current date in America/Bogota timezone for comparison.
        Only subscriptions with ACTIVE status are expired.

        Args:
            db: Database session

        Returns:
            int: Number of subscriptions expired
        """
        from app.utils.timezone import get_today_colombia
        
        # Get expired subscriptions
        expired_subscriptions = SubscriptionRepository.get_expired(db)
        
        if not expired_subscriptions:
            logger.info("No expired subscriptions found")
            return 0

        # Extract subscription IDs
        subscription_ids = [sub.id for sub in expired_subscriptions]
        
        # Batch update to EXPIRED status
        expired_count = SubscriptionRepository.expire_subscriptions_batch(
            db=db,
            subscription_ids=subscription_ids
        )

        logger.info(
            f"Expired {expired_count} subscription(s). "
            f"Reference date (Colombia): {get_today_colombia()}"
        )

        return expired_count

    @staticmethod
    def activate_scheduled_subscriptions(db: Session) -> int:
        """
        Transition scheduled subscriptions to PENDING_PAYMENT status when they reach their start_date.

        Uses the current date in America/Bogota timezone for comparison.
        Only subscriptions with SCHEDULED status are processed.
        Only processes subscriptions for clients that do NOT have an active subscription
        (to respect the constraint of one active subscription per client).

        Business rule: SCHEDULED -> PENDING_PAYMENT (when start_date arrives)
        The subscription will become ACTIVE once payment is completed.

        Args:
            db: Database session

        Returns:
            int: Number of subscriptions updated from SCHEDULED to PENDING_PAYMENT
        """
        from app.utils.timezone import get_today_colombia
        
        # Get scheduled subscriptions ready to activate
        ready_subscriptions = SubscriptionRepository.get_ready_to_activate(db)
        
        if not ready_subscriptions:
            logger.info("No scheduled subscriptions ready to transition to PENDING_PAYMENT")
            return 0

        # Filter subscriptions: only process if client doesn't have an active subscription
        subscriptions_to_process = []
        for sub in ready_subscriptions:
            active_subs = SubscriptionRepository.get_active_by_client(db, sub.client_id)
            if not active_subs:
                subscriptions_to_process.append(sub)
            else:
                logger.info(
                    f"Skipping subscription {sub.id} for client {sub.client_id}: "
                    f"client already has an active subscription"
                )

        if not subscriptions_to_process:
            logger.info("No scheduled subscriptions can be processed (all clients have active subscriptions)")
            return 0

        # Extract subscription IDs
        subscription_ids = [sub.id for sub in subscriptions_to_process]
        
        # Batch update from SCHEDULED to PENDING_PAYMENT status
        updated_count = SubscriptionRepository.activate_subscriptions_batch(
            db=db,
            subscription_ids=subscription_ids
        )

        logger.info(
            f"Updated {updated_count} scheduled subscription(s) from SCHEDULED to PENDING_PAYMENT. "
            f"Reference date (Colombia): {get_today_colombia()}"
        )

        return updated_count