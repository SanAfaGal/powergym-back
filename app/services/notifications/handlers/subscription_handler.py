"""
Subscription notification handler for PowerGym API.

This module handles all Telegram notifications related to subscription operations:
- Subscription creation
- Subscription updates
- Subscription cancellation
- Subscription renewal
"""

import logging
from decimal import Decimal
from typing import Optional

from app.services.notifications.handlers.base_handler import BaseNotificationHandler
from app.services.notifications.messages import (
    format_subscription_cancel_message,
    format_subscription_create_message,
    format_subscription_renew_message,
    format_subscription_update_message,
)

logger = logging.getLogger(__name__)


class SubscriptionNotificationHandler(BaseNotificationHandler):
    """
    Handler for subscription-related Telegram notifications.
    
    All methods are async and will gracefully handle errors
    without raising exceptions to the calling code.
    """
    
    @staticmethod
    async def notify_subscription_created(
        client_name: str,
        plan_name: str,
        start_date: str,
        end_date: str,
        plan_price: Decimal,
        status: str
    ) -> None:
        """
        Send Telegram notification for new subscription.
        
        Args:
            client_name: Full name of the client
            plan_name: Name of the subscription plan
            start_date: Subscription start date (formatted string)
            end_date: Subscription end date (formatted string)
            plan_price: Plan price
            status: Subscription status
        
        Returns:
            None (errors are logged but not raised)
        """
        try:
            message = format_subscription_create_message(
                client_name=client_name,
                plan_name=plan_name,
                start_date=start_date,
                end_date=end_date,
                plan_price=plan_price,
                status=status
            )
            await SubscriptionNotificationHandler._send_notification(message)
            logger.debug("Subscription creation notification sent for client: %s", client_name)
        except Exception as e:
            logger.error(
                "Error sending subscription creation notification: %s",
                str(e),
                exc_info=True
            )
    
    @staticmethod
    async def notify_subscription_updated(
        client_name: str,
        plan_name: str,
        subscription_id: str
    ) -> None:
        """
        Send Telegram notification for subscription update.
        
        Args:
            client_name: Full name of the client
            plan_name: Name of the subscription plan
            subscription_id: Subscription UUID
        
        Returns:
            None (errors are logged but not raised)
        """
        try:
            message = format_subscription_update_message(
                client_name=client_name,
                plan_name=plan_name,
                subscription_id=subscription_id
            )
            await SubscriptionNotificationHandler._send_notification(message)
            logger.debug("Subscription update notification sent for subscription: %s", subscription_id)
        except Exception as e:
            logger.error(
                "Error sending subscription update notification: %s",
                str(e),
                exc_info=True
            )
    
    @staticmethod
    async def notify_subscription_cancelled(
        client_name: str,
        plan_name: str,
        cancellation_reason: Optional[str] = None
    ) -> None:
        """
        Send Telegram notification for subscription cancellation.
        
        Args:
            client_name: Full name of the client
            plan_name: Name of the subscription plan
            cancellation_reason: Optional cancellation reason
        
        Returns:
            None (errors are logged but not raised)
        """
        try:
            message = format_subscription_cancel_message(
                client_name=client_name,
                plan_name=plan_name,
                cancellation_reason=cancellation_reason
            )
            await SubscriptionNotificationHandler._send_notification(message)
            logger.debug("Subscription cancellation notification sent for client: %s", client_name)
        except Exception as e:
            logger.error(
                "Error sending subscription cancellation notification: %s",
                str(e),
                exc_info=True
            )
    
    @staticmethod
    async def notify_subscription_renewed(
        client_name: str,
        plan_name: str,
        start_date: str,
        end_date: str
    ) -> None:
        """
        Send Telegram notification for subscription renewal.
        
        Args:
            client_name: Full name of the client
            plan_name: Name of the subscription plan
            start_date: New subscription start date
            end_date: New subscription end date
        
        Returns:
            None (errors are logged but not raised)
        """
        try:
            message = format_subscription_renew_message(
                client_name=client_name,
                plan_name=plan_name,
                start_date=start_date,
                end_date=end_date
            )
            await SubscriptionNotificationHandler._send_notification(message)
            logger.debug("Subscription renewal notification sent for client: %s", client_name)
        except Exception as e:
            logger.error(
                "Error sending subscription renewal notification: %s",
                str(e),
                exc_info=True
            )

