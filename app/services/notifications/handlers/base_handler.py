"""
Base notification handler for PowerGym API.

This module provides a base class for all notification handlers,
containing common functionality for sending Telegram notifications.
"""

import logging
from abc import ABC
from typing import Optional

from app.core.config import settings
from app.utils.telegram_client import send_telegram_message

logger = logging.getLogger(__name__)


class BaseNotificationHandler(ABC):
    """
    Base class for all notification handlers.
    
    Provides common functionality for sending Telegram notifications,
    including configuration checks and error handling.
    """
    
    @staticmethod
    async def _send_notification(message: str) -> None:
        """
        Send a Telegram notification message.
        
        This method handles all common logic for sending notifications:
        - Checks if Telegram is enabled
        - Validates chat ID configuration
        - Sends the message asynchronously
        - Logs errors without raising exceptions
        
        Args:
            message: The formatted message to send
        
        Returns:
            None (errors are logged but not raised)
        """
        if not settings.TELEGRAM_CHAT_ID:
            logger.debug("Telegram chat ID not configured, skipping notification")
            return
        
        try:
            await send_telegram_message(settings.TELEGRAM_CHAT_ID, message)
            logger.debug("Telegram notification sent successfully")
        except Exception as e:
            logger.error(
                "Error sending Telegram notification: %s",
                str(e),
                exc_info=True
            )

