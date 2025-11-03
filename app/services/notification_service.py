"""
Notification Service for PowerGym API.

This service handles all Telegram notifications for various events in the system,
including check-ins, payments, subscriptions, client registrations, and inventory sales.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.utils.telegram_client import send_telegram_message
from app.utils.common.formatters import (
    format_currency,
    format_client_name,
    format_time,
    format_quantity,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending Telegram notifications.
    
    All notification methods are async and will gracefully handle errors
    without raising exceptions to the calling code.
    """

    @staticmethod
    async def send_check_in_notification(
        client_name: str,
        dni_number: str,
        check_in_time: datetime
    ) -> None:
        """
        Send Telegram notification for client check-in.

        Args:
            client_name: Full name of the client
            dni_number: Client's DNI number
            check_in_time: Datetime of the check-in

        Returns:
            None (errors are logged but not raised)
        """
        if not settings.TELEGRAM_CHAT_ID:
            logger.debug("Telegram chat ID not configured, skipping check-in notification")
            return

        try:
            time_str = format_time(check_in_time)

            message = (
                f"🏋️ *Check-in*\n"
                f"Client: {client_name}\n"
                f"DNI: {dni_number}\n"
                f"Time: {time_str}"
            )

            await send_telegram_message(settings.TELEGRAM_CHAT_ID, message)
            logger.debug("Check-in notification sent for client: %s", client_name)
        except Exception as e:
            logger.error(
                "Error sending check-in notification to Telegram: %s",
                str(e),
                exc_info=True
            )

    @staticmethod
    async def send_payment_notification(
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
        if not settings.TELEGRAM_CHAT_ID:
            logger.debug("Telegram chat ID not configured, skipping payment notification")
            return

        try:
            amount_str = format_currency(amount)
            debt_str = format_currency(remaining_debt) if remaining_debt is not None else "$0.00"

            # Map payment method to display name
            method_map = {
                "cash": "Cash",
                "card": "Card",
                "transfer": "Transfer",
                "qr": "QR"
            }
            method_str = method_map.get(payment_method.lower(), payment_method)

            message = (
                f"💰 *Payment Received*\n"
                f"Client: {client_name}\n"
                f"Amount: {amount_str}\n"
                f"Method: {method_str}\n"
                f"Subscription: {plan_name}\n"
                f"Remaining debt: {debt_str}"
            )

            await send_telegram_message(settings.TELEGRAM_CHAT_ID, message)
            logger.debug("Payment notification sent for client: %s", client_name)
        except Exception as e:
            logger.error(
                "Error sending payment notification to Telegram: %s",
                str(e),
                exc_info=True
            )

    @staticmethod
    async def send_subscription_notification(
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
            status: Subscription status (pending_payment, active, expired, cancelled)

        Returns:
            None (errors are logged but not raised)
        """
        if not settings.TELEGRAM_CHAT_ID:
            logger.debug("Telegram chat ID not configured, skipping subscription notification")
            return

        try:
            price_str = format_currency(plan_price)

            # Map status to display name
            status_map = {
                "pending_payment": "Pending Payment",
                "active": "Active",
                "expired": "Expired",
                "cancelled": "Cancelled"
            }
            status_str = status_map.get(status.lower(), status)

            message = (
                f"📋 *New Subscription*\n"
                f"Client: {client_name}\n"
                f"Plan: {plan_name}\n"
                f"Start: {start_date}\n"
                f"End: {end_date}\n"
                f"Price: {price_str}\n"
                f"Status: {status_str}"
            )

            await send_telegram_message(settings.TELEGRAM_CHAT_ID, message)
            logger.debug("Subscription notification sent for client: %s", client_name)
        except Exception as e:
            logger.error(
                "Error sending subscription notification to Telegram: %s",
                str(e),
                exc_info=True
            )

    @staticmethod
    async def send_client_registration_notification(
        first_name: str,
        last_name: str,
        dni_number: str,
        phone: str,
        middle_name: Optional[str] = None,
        second_last_name: Optional[str] = None
    ) -> None:
        """
        Send Telegram notification for new client registration.

        Args:
            first_name: Client's first name
            last_name: Client's last name
            dni_number: Client's DNI number
            phone: Client's phone number
            middle_name: Client's middle name (optional)
            second_last_name: Client's second last name (optional)

        Returns:
            None (errors are logged but not raised)
        """
        if not settings.TELEGRAM_CHAT_ID:
            logger.debug("Telegram chat ID not configured, skipping client registration notification")
            return

        try:
            client_name = format_client_name(
                first_name,
                last_name,
                middle_name,
                second_last_name
            )

            message = (
                f"👤 *New Client Registered*\n"
                f"Name: {client_name}\n"
                f"DNI: {dni_number}\n"
                f"Phone: {phone}"
            )

            await send_telegram_message(settings.TELEGRAM_CHAT_ID, message)
            logger.debug("Client registration notification sent for: %s", client_name)
        except Exception as e:
            logger.error(
                "Error sending client registration notification to Telegram: %s",
                str(e),
                exc_info=True
            )

    @staticmethod
    async def send_inventory_sale_notification(
        product_name: str,
        quantity: Decimal,
        unit_price: Decimal,
        total: Decimal,
        responsible: Optional[str] = None
    ) -> None:
        """
        Send Telegram notification for inventory sale (EXIT movement).

        Args:
            product_name: Name of the product sold
            quantity: Quantity sold
            unit_price: Unit price of the product
            total: Total sale amount
            responsible: Name of the person responsible (optional)

        Returns:
            None (errors are logged but not raised)
        """
        if not settings.TELEGRAM_CHAT_ID:
            logger.debug("Telegram chat ID not configured, skipping inventory sale notification")
            return

        try:
            unit_price_str = format_currency(unit_price)
            total_str = format_currency(total)
            quantity_str = format_quantity(quantity, "units")

            message = (
                f"🛒 *Product Sale*\n"
                f"Product: {product_name}\n"
                f"Quantity: {quantity_str}\n"
                f"Unit price: {unit_price_str}\n"
                f"Total: {total_str}"
            )

            if responsible:
                message += f"\nResponsible: {responsible}"

            await send_telegram_message(settings.TELEGRAM_CHAT_ID, message)
            logger.debug("Inventory sale notification sent for product: %s", product_name)
        except Exception as e:
            logger.error(
                "Error sending inventory sale notification to Telegram: %s",
                str(e),
                exc_info=True
            )
