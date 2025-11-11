"""
Reward notification handler for PowerGym API.

This module handles all Telegram notifications related to reward operations:
- Reward redemption
"""

import logging
from decimal import Decimal

from app.services.notifications.handlers.base_handler import BaseNotificationHandler
from app.services.notifications.messages import format_reward_redeem_message

logger = logging.getLogger(__name__)


class RewardNotificationHandler(BaseNotificationHandler):
    """
    Handler for reward-related Telegram notifications.
    
    All methods are async and will gracefully handle errors
    without raising exceptions to the calling code.
    """
    
    @staticmethod
    async def notify_reward_redeemed(
        client_name: str,
        discount_percentage: Decimal,
        subscription_plan: str
    ) -> None:
        """
        Send Telegram notification for reward redemption.
        
        Args:
            client_name: Full name of the client
            discount_percentage: Discount percentage applied
            subscription_plan: Name of the subscription plan where reward was applied
        
        Returns:
            None (errors are logged but not raised)
        """
        try:
            message = format_reward_redeem_message(
                client_name=client_name,
                discount_percentage=discount_percentage,
                subscription_plan=subscription_plan
            )
            await RewardNotificationHandler._send_notification(message)
            logger.debug("Reward redemption notification sent for client: %s", client_name)
        except Exception as e:
            logger.error(
                "Error sending reward redemption notification: %s",
                str(e),
                exc_info=True
            )

