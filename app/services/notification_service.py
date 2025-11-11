"""
Notification Service for PowerGym API.

This service provides a unified interface for sending Telegram notifications
for various events in the system. It delegates to specialized handlers for
each domain (clients, subscriptions, payments, rewards, inventory, attendance).

All notification methods are async and will gracefully handle errors
without raising exceptions to the calling code.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.services.notifications.handlers.attendance_handler import AttendanceNotificationHandler
from app.services.notifications.handlers.client_handler import ClientNotificationHandler
from app.services.notifications.handlers.inventory_handler import InventoryNotificationHandler
from app.services.notifications.handlers.payment_handler import PaymentNotificationHandler
from app.services.notifications.handlers.reward_handler import RewardNotificationHandler
from app.services.notifications.handlers.subscription_handler import SubscriptionNotificationHandler

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Unified service for sending Telegram notifications.
    
    This class provides a facade pattern, delegating to specialized handlers
    for each domain. All methods are async and will gracefully handle errors
    without raising exceptions to the calling code.
    """

    # ============================================================================
    # CLIENT NOTIFICATIONS
    # ============================================================================

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
        from app.utils.common.formatters import format_client_name
        
        client_name = format_client_name(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            second_last_name=second_last_name
        )
        
        await ClientNotificationHandler.notify_client_created(
            client_name=client_name,
            dni_number=dni_number,
            phone=phone
        )

    @staticmethod
    async def send_client_update_notification(
        first_name: str,
        last_name: str,
        dni_number: str,
        middle_name: Optional[str] = None,
        second_last_name: Optional[str] = None
    ) -> None:
        """
        Send Telegram notification for client update.

        Args:
            first_name: Client's first name
            last_name: Client's last name
            dni_number: Client's DNI number
            middle_name: Client's middle name (optional)
            second_last_name: Client's second last name (optional)

        Returns:
            None (errors are logged but not raised)
        """
        from app.utils.common.formatters import format_client_name
        
        client_name = format_client_name(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            second_last_name=second_last_name
        )
        
        await ClientNotificationHandler.notify_client_updated(
            client_name=client_name,
            dni_number=dni_number
        )

    @staticmethod
    async def send_client_delete_notification(
        first_name: str,
        last_name: str,
        dni_number: str,
        middle_name: Optional[str] = None,
        second_last_name: Optional[str] = None
    ) -> None:
        """
        Send Telegram notification for client deletion.

        Args:
            first_name: Client's first name
            last_name: Client's last name
            dni_number: Client's DNI number
            middle_name: Client's middle name (optional)
            second_last_name: Client's second last name (optional)

        Returns:
            None (errors are logged but not raised)
        """
        from app.utils.common.formatters import format_client_name
        
        client_name = format_client_name(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            second_last_name=second_last_name
        )
        
        await ClientNotificationHandler.notify_client_deleted(
            client_name=client_name,
            dni_number=dni_number
        )

    # ============================================================================
    # SUBSCRIPTION NOTIFICATIONS
    # ============================================================================

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
        await SubscriptionNotificationHandler.notify_subscription_created(
            client_name=client_name,
            plan_name=plan_name,
            start_date=start_date,
            end_date=end_date,
            plan_price=plan_price,
            status=status
        )

    @staticmethod
    async def send_subscription_cancel_notification(
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
        await SubscriptionNotificationHandler.notify_subscription_cancelled(
            client_name=client_name,
            plan_name=plan_name,
            cancellation_reason=cancellation_reason
        )

    @staticmethod
    async def send_subscription_renew_notification(
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
        await SubscriptionNotificationHandler.notify_subscription_renewed(
            client_name=client_name,
            plan_name=plan_name,
            start_date=start_date,
            end_date=end_date
        )

    # ============================================================================
    # PAYMENT NOTIFICATIONS
    # ============================================================================

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
        await PaymentNotificationHandler.notify_payment_created(
            client_name=client_name,
            amount=amount,
            payment_method=payment_method,
            plan_name=plan_name,
            remaining_debt=remaining_debt
        )

    @staticmethod
    async def send_payment_update_notification(
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
        await PaymentNotificationHandler.notify_payment_updated(
            client_name=client_name,
            amount=amount,
            payment_id=payment_id
        )

    @staticmethod
    async def send_payment_delete_notification(
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
        await PaymentNotificationHandler.notify_payment_deleted(
            client_name=client_name,
            amount=amount,
            payment_id=payment_id
        )

    # ============================================================================
    # REWARD NOTIFICATIONS
    # ============================================================================

    @staticmethod
    async def send_reward_redemption_notification(
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
        await RewardNotificationHandler.notify_reward_redeemed(
            client_name=client_name,
            discount_percentage=discount_percentage,
            subscription_plan=subscription_plan
        )

    # ============================================================================
    # INVENTORY NOTIFICATIONS
    # ============================================================================

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
        await InventoryNotificationHandler.notify_stock_removed(
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
            total=total,
            responsible=responsible
        )

    @staticmethod
    async def send_product_create_notification(
        product_name: str,
        price: Decimal,
        initial_stock: Decimal
    ) -> None:
        """
        Send Telegram notification for product creation.

        Args:
            product_name: Name of the product
            price: Product price
            initial_stock: Initial stock quantity

        Returns:
            None (errors are logged but not raised)
        """
        await InventoryNotificationHandler.notify_product_created(
            product_name=product_name,
            price=price,
            initial_stock=initial_stock
        )

    @staticmethod
    async def send_product_update_notification(
        product_name: str,
        product_id: str
    ) -> None:
        """
        Send Telegram notification for product update.

        Args:
            product_name: Name of the product
            product_id: Product UUID

        Returns:
            None (errors are logged but not raised)
        """
        await InventoryNotificationHandler.notify_product_updated(
            product_name=product_name,
            product_id=product_id
        )

    @staticmethod
    async def send_product_delete_notification(
        product_name: str,
        product_id: str
    ) -> None:
        """
        Send Telegram notification for product deletion.

        Args:
            product_name: Name of the product
            product_id: Product UUID

        Returns:
            None (errors are logged but not raised)
        """
        await InventoryNotificationHandler.notify_product_deleted(
            product_name=product_name,
            product_id=product_id
        )

    @staticmethod
    async def send_stock_add_notification(
        product_name: str,
        quantity: Decimal,
        new_stock: Decimal,
        notes: Optional[str] = None
    ) -> None:
        """
        Send Telegram notification for stock addition.

        Args:
            product_name: Name of the product
            quantity: Quantity added
            new_stock: New total stock after addition
            notes: Optional notes about the addition

        Returns:
            None (errors are logged but not raised)
        """
        await InventoryNotificationHandler.notify_stock_added(
            product_name=product_name,
            quantity=quantity,
            new_stock=new_stock,
            notes=notes
        )

    # ============================================================================
    # ATTENDANCE NOTIFICATIONS
    # ============================================================================

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
        await AttendanceNotificationHandler.notify_check_in(
            client_name=client_name,
            dni_number=dni_number,
            check_in_time=check_in_time
        )
