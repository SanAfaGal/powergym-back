"""
Payment notification handler for PowerGym API.

This module handles all Telegram notifications related to payment operations:
- Payment creation
- Payment updates
- Payment deletion
"""

import logging
from decimal import Decimal
from typing import Optional

from app.services.notifications.handlers.base_handler import BaseNotificationHandler
from app.services.notifications.messages import (
    format_payment_create_message,
    format_payment_delete_message,
    format_payment_update_message,
)

logger = logging.getLogger(__name__)


class PaymentNotificationHandler(BaseNotificationHandler):
    """
    Handler for payment-related Telegram notifications.
    
    All methods are async and will gracefully handle errors
    without raising exceptions to the calling code.
    """
    
    @staticmethod
    async def notify_payment_created(
        client_name: str,
        amount: Decimal,
        payment_method: str,
        plan_name: str,
        remaining_debt: Optional[Decimal] = None
    ) -> None:
        """
        Send Telegram notification for payment received.
        
        Args:
            client_name: Full name of the client
            amount: Payment amount
            payment_method: Payment method used (cash, card, transfer, qr)
            plan_name: Name of the subscription plan
            remaining_debt: Remaining debt amount (optional)
        
        Returns:
            None (errors are logged but not raised)
        """
        try:
            message = format_payment_create_message(
                client_name=client_name,
                amount=amount,
                payment_method=payment_method,
                plan_name=plan_name,
                remaining_debt=remaining_debt
            )
            await PaymentNotificationHandler._send_notification(message)
            logger.debug("Payment creation notification sent for client: %s", client_name)
        except Exception as e:
            logger.error(
                "Error sending payment creation notification: %s",
                str(e),
                exc_info=True
            )
    
    @staticmethod
    async def notify_payment_updated(
        client_name: str,
        amount: Decimal,
        payment_id: str
    ) -> None:
        """
        Send Telegram notification for payment update.
        
        Args:
            client_name: Full name of the client
            amount: Updated payment amount
            payment_id: Payment UUID
        
        Returns:
            None (errors are logged but not raised)
        """
        try:
            message = format_payment_update_message(
                client_name=client_name,
                amount=amount,
                payment_id=payment_id
            )
            await PaymentNotificationHandler._send_notification(message)
            logger.debug("Payment update notification sent for payment: %s", payment_id)
        except Exception as e:
            logger.error(
                "Error sending payment update notification: %s",
                str(e),
                exc_info=True
            )
    
    @staticmethod
    async def notify_payment_deleted(
        client_name: str,
        amount: Decimal,
        payment_id: str
    ) -> None:
        """
        Send Telegram notification for payment deletion.
        
        Args:
            client_name: Full name of the client
            amount: Deleted payment amount
            payment_id: Payment UUID
        
        Returns:
            None (errors are logged but not raised)
        """
        try:
            message = format_payment_delete_message(
                client_name=client_name,
                amount=amount,
                payment_id=payment_id
            )
            await PaymentNotificationHandler._send_notification(message)
            logger.debug("Payment deletion notification sent for payment: %s", payment_id)
        except Exception as e:
            logger.error(
                "Error sending payment deletion notification: %s",
                str(e),
                exc_info=True
            )

