"""
Attendance notification handler for PowerGym API.

This module handles all Telegram notifications related to attendance operations:
- Check-in notifications
"""

import logging
from datetime import datetime

from app.services.notifications.handlers.base_handler import BaseNotificationHandler
from app.services.notifications.messages import format_check_in_message

logger = logging.getLogger(__name__)


class AttendanceNotificationHandler(BaseNotificationHandler):
    """
    Handler for attendance-related Telegram notifications.
    
    All methods are async and will gracefully handle errors
    without raising exceptions to the calling code.
    """
    
    @staticmethod
    async def notify_check_in(
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
        try:
            message = format_check_in_message(
                client_name=client_name,
                dni_number=dni_number,
                check_in_time=check_in_time
            )
            await AttendanceNotificationHandler._send_notification(message)
            logger.debug("Check-in notification sent for client: %s", client_name)
        except Exception as e:
            logger.error(
                "Error sending check-in notification: %s",
                str(e),
                exc_info=True
            )

