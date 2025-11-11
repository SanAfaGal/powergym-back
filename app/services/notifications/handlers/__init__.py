"""
Notification handlers for PowerGym API.

This module contains specialized notification handlers for different domains,
each responsible for sending Telegram notifications for specific operations.
"""

from app.services.notifications.handlers.attendance_handler import AttendanceNotificationHandler
from app.services.notifications.handlers.client_handler import ClientNotificationHandler
from app.services.notifications.handlers.inventory_handler import InventoryNotificationHandler
from app.services.notifications.handlers.payment_handler import PaymentNotificationHandler
from app.services.notifications.handlers.reward_handler import RewardNotificationHandler
from app.services.notifications.handlers.subscription_handler import SubscriptionNotificationHandler

__all__ = [
    "AttendanceNotificationHandler",
    "ClientNotificationHandler",
    "InventoryNotificationHandler",
    "PaymentNotificationHandler",
    "RewardNotificationHandler",
    "SubscriptionNotificationHandler",
]

