# Standard library imports
import logging
from datetime import datetime, timedelta, date, timezone
from decimal import Decimal
from typing import List
from uuid import UUID

# Third-party imports
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

# Local imports
from app.core.config import settings
from app.db.models import AttendanceModel, DurationTypeEnum
from app.repositories.plan_repository import PlanRepository
from app.repositories.reward_repository import RewardRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.schemas.reward import Reward, RewardApplyInput, RewardEligibilityResponse
from app.utils.timezone import get_current_utc_datetime, get_today_colombia

logger = logging.getLogger(__name__)


class RewardService:
    """
    Business logic for rewards management.
    
    Handles reward eligibility calculation, application, and retrieval.
    Uses configuration from environment variables for reward rules.
    """

    @staticmethod
    def _is_plan_eligible(plan_duration_unit: DurationTypeEnum) -> bool:
        """
        Check if a plan duration unit is eligible for rewards.
        
        Args:
            plan_duration_unit: The plan's duration unit enum value
            
        Returns:
            True if the plan unit is eligible for rewards, False otherwise
        """
        eligible_units = settings.REWARD_ELIGIBLE_PLAN_UNITS
        # Convert enum value to lowercase string for comparison
        unit_str = plan_duration_unit.value.lower()
        return unit_str in eligible_units

    @staticmethod
    def calculate_eligibility(db: Session, subscription_id: UUID) -> RewardEligibilityResponse:
        """
        Calculate eligibility for a reward based on subscription cycle.

        Business Rules:
        - Subscription must exist (can be active or terminated)
        - Plan must be in eligible duration units (configurable via REWARD_ELIGIBLE_PLAN_UNITS)
        - Count attendances in cycle: 
          * If subscription ended: WHERE client_id = X AND check_in >= subscription.start_date AND check_in <= subscription.end_date
          * If subscription active: WHERE client_id = X AND check_in >= subscription.start_date AND check_in <= today
        - If COUNT >= threshold (REWARD_ATTENDANCE_THRESHOLD) and no reward exists, create reward
        - Reward expires after configured days (REWARD_EXPIRATION_DAYS) from eligible_date

        Args:
            db: Database session
            subscription_id: Subscription UUID

        Returns:
            RewardEligibilityResponse: Eligibility information

        Raises:
            HTTPException: If subscription or plan not found
        """
        try:
            # Get subscription
            subscription = SubscriptionRepository.get_by_id(db, subscription_id)
            if not subscription:
                logger.warning(f"Subscription not found: {subscription_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Subscription {subscription_id} not found"
                )

            # Get plan
            plan_id = subscription.plan_id
            plan = PlanRepository.get_by_id(db, plan_id)
            if not plan:
                logger.warning(f"Plan not found: {plan_id} for subscription {subscription_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Plan {plan_id} not found"
                )

            # Verify plan is eligible for rewards
            if not RewardService._is_plan_eligible(plan.duration_unit):
                logger.debug(
                    f"Plan {plan_id} with duration_unit '{plan.duration_unit.value}' "
                    f"is not eligible for rewards. Eligible units: {settings.REWARD_ELIGIBLE_PLAN_UNITS}"
                )
                return RewardEligibilityResponse(
                    eligible=False,
                    attendance_count=0,
                    reward_id=None,
                    expires_at=None
                )

            # Check if reward already exists for this subscription
            if RewardRepository.exists_for_subscription(db, subscription_id):
                # Get existing reward to return info
                existing_rewards = RewardRepository.get_by_subscription_id(db, subscription_id)
                if existing_rewards:
                    existing_reward = existing_rewards[0]
                    logger.debug(
                        f"Existing reward found for subscription {subscription_id}: {existing_reward.id}"
                    )
                    return RewardEligibilityResponse(
                        eligible=True,
                        attendance_count=existing_reward.attendance_count,
                        reward_id=existing_reward.id,
                        expires_at=existing_reward.expires_at
                    )

            # Count attendances in cycle
            # For active subscriptions: count from start_date to today
            # For terminated subscriptions: count from start_date to end_date
            today = get_today_colombia()
            start_date = subscription.start_date
            end_date = subscription.end_date
            client_id = subscription.client_id
            
            # Use today if subscription is still active, otherwise use end_date
            count_end_date = min(end_date, today)
            
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(count_end_date, datetime.max.time())

            attendance_count = db.query(AttendanceModel).filter(
                AttendanceModel.client_id == client_id,
                AttendanceModel.check_in >= start_datetime,
                AttendanceModel.check_in <= end_datetime
            ).count()

            logger.debug(
                f"Attendance count for subscription {subscription_id}: {attendance_count} "
                f"(threshold: {settings.REWARD_ATTENDANCE_THRESHOLD})"
            )

            # Check eligibility against configured threshold
            if attendance_count < settings.REWARD_ATTENDANCE_THRESHOLD:
                return RewardEligibilityResponse(
                    eligible=False,
                    attendance_count=attendance_count,
                    reward_id=None,
                    expires_at=None
                )

            # Create reward
            # eligible_date is today if subscription is active, otherwise end_date
            eligible_date = today if subscription.end_date > today else end_date
            # Create timezone-aware datetime for expires_at using configured expiration days
            expires_at_naive = datetime.combine(eligible_date, datetime.min.time()) + timedelta(
                days=settings.REWARD_EXPIRATION_DAYS
            )
            expires_at = expires_at_naive.replace(tzinfo=timezone.utc)

            reward = RewardRepository.create(
                db=db,
                subscription_id=subscription_id,
                client_id=client_id,
                attendance_count=attendance_count,
                discount_percentage=float(Decimal(str(settings.REWARD_DISCOUNT_PERCENTAGE))),
                eligible_date=eligible_date,
                expires_at=expires_at
            )

            logger.info(
                f"Reward created for subscription {subscription_id}: {reward.id} "
                f"(attendance_count={attendance_count}, discount={settings.REWARD_DISCOUNT_PERCENTAGE}%, "
                f"expires_at={expires_at})"
            )

            return RewardEligibilityResponse(
                eligible=True,
                attendance_count=attendance_count,
                reward_id=reward.id,
                expires_at=reward.expires_at
            )
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error calculating reward eligibility for subscription {subscription_id}: {str(e)}",
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error calculating reward eligibility: {str(e)}"
            )

    @staticmethod
    def get_available_rewards(db: Session, client_id: UUID) -> List[Reward]:
        """
        Get available rewards for a client.

        Available means: status='pending' and expires_at > NOW()

        Args:
            db: Database session
            client_id: Client UUID

        Returns:
            List[Reward]: List of available rewards
        """
        rewards = RewardRepository.get_available_by_client(db, client_id)
        return [Reward.from_orm(reward) for reward in rewards]

    @staticmethod
    def apply_reward(
            db: Session,
            reward_id: UUID,
            apply_data: RewardApplyInput
    ) -> Reward:
        """
        Apply a reward to a subscription.

        Validations:
        - Reward exists
        - Reward status is 'pending'
        - Reward is not expired (expires_at > NOW())
        - Subscription exists

        Args:
            db: Database session
            reward_id: Reward UUID
            apply_data: RewardApplyInput with subscription_id and discount_percentage

        Returns:
            Reward: Updated reward
        """
        # Get reward
        reward = RewardRepository.get_by_id(db, reward_id)
        if not reward:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reward {reward_id} not found"
            )

        # Validate status
        if reward.status.value != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Reward {reward_id} is not in pending status. Current status: {reward.status.value}"
            )

        # Validate expiration
        now = get_current_utc_datetime()
        if reward.expires_at <= now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Reward {reward_id} has expired"
            )

        # Validate subscription exists
        subscription = SubscriptionRepository.get_by_id(db, apply_data.subscription_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription {apply_data.subscription_id} not found"
            )

        # Apply reward
        updated_reward = RewardRepository.apply_reward(
            db=db,
            reward_id=reward_id,
            subscription_id=apply_data.subscription_id,
            discount_percentage=apply_data.discount_percentage
        )

        if not updated_reward:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to apply reward {reward_id}"
            )

        logger.info(f"Reward {reward_id} applied to subscription {apply_data.subscription_id}")

        # Send Telegram notification in background
        try:
            from app.services.notification_service import NotificationService
            from app.core.async_processing import run_async_in_background
            from app.utils.common.formatters import format_client_name
            from app.repositories.client_repository import ClientRepository
            
            # Get client and plan information
            client = ClientRepository.get_by_id(db, reward.client_id)
            plan = PlanRepository.get_by_id(db, subscription.plan_id)
            
            if client and plan:
                client_name = format_client_name(
                    first_name=client.first_name,
                    last_name=client.last_name,
                    middle_name=client.middle_name,
                    second_last_name=client.second_last_name
                )
                
                # Send notification asynchronously (fire and forget)
                run_async_in_background(
                    NotificationService.send_reward_redemption_notification(
                        client_name=client_name,
                        discount_percentage=Decimal(str(apply_data.discount_percentage)),
                        subscription_plan=plan.name
                    )
                )
        except Exception as e:
            # Log error but don't fail the reward application
            logger.error("Error sending reward redemption notification: %s", str(e), exc_info=True)

        return Reward.from_orm(updated_reward)

    @staticmethod
    def get_rewards_by_subscription(db: Session, subscription_id: UUID) -> List[Reward]:
        """
        Get all rewards for a subscription.

        Args:
            db: Database session
            subscription_id: Subscription UUID

        Returns:
            List[Reward]: List of rewards
        """
        rewards = RewardRepository.get_by_subscription_id(db, subscription_id)
        return [Reward.from_orm(reward) for reward in rewards]

    @staticmethod
    def expire_rewards(db: Session) -> int:
        """
        Mark expired pending rewards as expired.

        This can be called by a cron job or manually.

        Args:
            db: Database session

        Returns:
            int: Number of rewards expired
        """
        expired_rewards = RewardRepository.get_expired_pending(db)
        if not expired_rewards:
            return 0

        reward_ids: List[UUID] = [reward.id for reward in expired_rewards]
        count = RewardRepository.expire_rewards(db, reward_ids)

        logger.info(f"Expired {count} rewards")
        return count

