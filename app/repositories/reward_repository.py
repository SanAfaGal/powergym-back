from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from app.db.models import RewardModel, RewardStatusEnum
import logging

logger = logging.getLogger(__name__)


class RewardRepository:
    """Data access layer for rewards"""

    @staticmethod
    def create(
            db: Session,
            subscription_id: UUID,
            client_id: UUID,
            attendance_count: int,
            discount_percentage: float,
            eligible_date,
            expires_at: datetime
    ) -> RewardModel:
        """
        Create a new reward.

        Args:
            db: Database session
            subscription_id: Subscription UUID that generated the reward
            client_id: Client UUID
            attendance_count: Number of attendances that qualified
            discount_percentage: Discount percentage (default 20.00)
            eligible_date: Date when the reward became eligible
            expires_at: Expiration datetime

        Returns:
            RewardModel: Created reward
        """
        try:
            reward = RewardModel(
                subscription_id=subscription_id,
                client_id=client_id,
                attendance_count=attendance_count,
                discount_percentage=discount_percentage,
                eligible_date=eligible_date,
                expires_at=expires_at,
                status=RewardStatusEnum.PENDING
            )
            db.add(reward)
            db.commit()
            db.refresh(reward)

            logger.info(f"Reward created: {reward.id} for subscription {subscription_id}")
            return reward

        except Exception as e:
            db.rollback()
            logger.error(f"Error creating reward: {str(e)}")
            raise

    @staticmethod
    def get_by_id(db: Session, reward_id: UUID) -> Optional[RewardModel]:
        """
        Get reward by ID.

        Args:
            db: Database session
            reward_id: Reward UUID

        Returns:
            RewardModel or None
        """
        return db.query(RewardModel).filter(
            RewardModel.id == reward_id
        ).first()

    @staticmethod
    def get_by_subscription_id(db: Session, subscription_id: UUID) -> List[RewardModel]:
        """
        Get all rewards for a subscription.

        Args:
            db: Database session
            subscription_id: Subscription UUID

        Returns:
            List[RewardModel]: List of rewards
        """
        return db.query(RewardModel).filter(
            RewardModel.subscription_id == subscription_id
        ).order_by(RewardModel.created_at.desc()).all()

    @staticmethod
    def get_available_by_client(db: Session, client_id: UUID) -> List[RewardModel]:
        """
        Get available rewards for a client.

        Available means:
        - status = 'pending'
        - expires_at > NOW()

        Args:
            db: Database session
            client_id: Client UUID

        Returns:
            List[RewardModel]: List of available rewards
        """
        now = datetime.utcnow()
        return db.query(RewardModel).filter(
            and_(
                RewardModel.client_id == client_id,
                RewardModel.status == RewardStatusEnum.PENDING,
                RewardModel.expires_at > now
            )
        ).order_by(RewardModel.expires_at.asc()).all()

    @staticmethod
    def apply_reward(
            db: Session,
            reward_id: UUID,
            subscription_id: UUID,
            discount_percentage: float
    ) -> Optional[RewardModel]:
        """
        Apply a reward to a subscription.

        Updates:
        - status = 'applied'
        - applied_at = NOW()
        - applied_subscription_id = subscription_id

        Args:
            db: Database session
            reward_id: Reward UUID
            subscription_id: Subscription UUID where the reward is applied
            discount_percentage: Discount percentage to apply

        Returns:
            RewardModel or None if not found
        """
        try:
            reward = RewardRepository.get_by_id(db, reward_id)
            if not reward:
                return None

            reward.status = RewardStatusEnum.APPLIED
            reward.applied_at = datetime.utcnow()
            reward.applied_subscription_id = subscription_id
            reward.discount_percentage = discount_percentage

            db.commit()
            db.refresh(reward)

            logger.info(f"Reward applied: {reward_id} to subscription {subscription_id}")
            return reward

        except Exception as e:
            db.rollback()
            logger.error(f"Error applying reward {reward_id}: {str(e)}")
            raise

    @staticmethod
    def get_expired_pending(db: Session) -> List[RewardModel]:
        """
        Get expired pending rewards (for cleanup job).

        Args:
            db: Database session

        Returns:
            List[RewardModel]: List of expired pending rewards
        """
        now = datetime.utcnow()
        return db.query(RewardModel).filter(
            and_(
                RewardModel.status == RewardStatusEnum.PENDING,
                RewardModel.expires_at <= now
            )
        ).all()

    @staticmethod
    def expire_rewards(db: Session, reward_ids: List[UUID]) -> int:
        """
        Mark rewards as expired.

        Args:
            db: Database session
            reward_ids: List of reward UUIDs to expire

        Returns:
            int: Number of rewards expired
        """
        try:
            count = db.query(RewardModel).filter(
                RewardModel.id.in_(reward_ids)
            ).update(
                {RewardModel.status: RewardStatusEnum.EXPIRED},
                synchronize_session=False
            )
            db.commit()

            logger.info(f"Expired {count} rewards")
            return count

        except Exception as e:
            db.rollback()
            logger.error(f"Error expiring rewards: {str(e)}")
            raise

    @staticmethod
    def exists_for_subscription(db: Session, subscription_id: UUID) -> bool:
        """
        Check if a reward already exists for a subscription.

        Args:
            db: Database session
            subscription_id: Subscription UUID

        Returns:
            bool: True if reward exists, False otherwise
        """
        count = db.query(func.count(RewardModel.id)).filter(
            RewardModel.subscription_id == subscription_id
        ).scalar() or 0
        return count > 0

