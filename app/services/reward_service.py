from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timedelta, date
from typing import List
from decimal import Decimal
from datetime import timezone

from fastapi import HTTPException, status
from app.repositories.reward_repository import RewardRepository
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.plan_repository import PlanRepository
from app.db.models import DurationTypeEnum, AttendanceModel
from app.schemas.reward import Reward, RewardEligibilityResponse, RewardApplyInput
import logging

logger = logging.getLogger(__name__)


class RewardService:
    """Business logic for rewards"""

    @staticmethod
    def calculate_eligibility(db: Session, subscription_id: UUID) -> RewardEligibilityResponse:
        """
        Calculate eligibility for a reward based on subscription cycle.

        Business Rules:
        - Subscription must exist and be terminated (end_date <= today)
        - Plan must be monthly (duration_unit == 'month')
        - Count attendances in cycle: WHERE client_id = X AND check_in >= subscription.start_date AND check_in <= subscription.end_date
        - If COUNT >= 20 and no reward exists for this subscription, create reward
        - Reward expires 7 days after eligible_date (end_date)

        Args:
            db: Database session
            subscription_id: Subscription UUID

        Returns:
            RewardEligibilityResponse: Eligibility information
        """
        # Get subscription
        subscription = SubscriptionRepository.get_by_id(db, subscription_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription {subscription_id} not found"
            )

        # Check if subscription is terminated
        today = date.today()
        if subscription.end_date > today:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Subscription {subscription_id} has not ended yet. End date: {subscription.end_date}"
            )

        # Get plan
        plan_id = subscription.plan_id
        plan = PlanRepository.get_by_id(db, plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan {plan_id} not found"
            )

        # Verify plan is monthly
        if plan.duration_unit != DurationTypeEnum.MONTH:
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
                reward_id = existing_reward.id
                expires_at_dt = existing_reward.expires_at
                return RewardEligibilityResponse(
                    eligible=True,
                    attendance_count=existing_reward.attendance_count,
                    reward_id=reward_id,
                    expires_at=expires_at_dt
                )

        # Count attendances in cycle
        # Query: WHERE client_id = X AND check_in >= subscription.start_date AND check_in <= subscription.end_date
        start_date = subscription.start_date
        end_date = subscription.end_date
        client_id = subscription.client_id
        
        from datetime import datetime as dt
        start_datetime = dt.combine(start_date, dt.min.time())
        end_datetime = dt.combine(end_date, dt.max.time())

        attendance_count = db.query(AttendanceModel).filter(
            AttendanceModel.client_id == client_id,
            AttendanceModel.check_in >= start_datetime,
            AttendanceModel.check_in <= end_datetime
        ).count()

        # Check eligibility (>= 20 attendances)
        if attendance_count < 20:
            return RewardEligibilityResponse(
                eligible=False,
                attendance_count=attendance_count,
                reward_id=None,
                expires_at=None
            )

        # Create reward
        eligible_date = end_date
        expires_at = dt.combine(eligible_date, dt.min.time()) + timedelta(days=7)

        reward = RewardRepository.create(
            db=db,
            subscription_id=subscription_id,
            client_id=client_id,
            attendance_count=attendance_count,
            discount_percentage=float(Decimal("20.00")),
            eligible_date=eligible_date,
            expires_at=expires_at
        )

        logger.info(f"Reward created for subscription {subscription_id}: {reward.id}")

        return RewardEligibilityResponse(
            eligible=True,
            attendance_count=attendance_count,
            reward_id=reward.id,
            expires_at=reward.expires_at
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
        now = datetime.now(timezone.utc)
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

