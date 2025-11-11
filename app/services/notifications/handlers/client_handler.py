"""
Client notification handler for PowerGym API.

This module handles all Telegram notifications related to client operations:
- Client creation
- Client updates
- Client deletion
"""

import logging
from typing import Optional

from app.services.notifications.handlers.base_handler import BaseNotificationHandler
from app.services.notifications.messages import (
    format_client_create_message,
    format_client_delete_message,
    format_client_update_message,
)

logger = logging.getLogger(__name__)


class ClientNotificationHandler(BaseNotificationHandler):
    """
    Handler for client-related Telegram notifications.
    
    All methods are async and will gracefully handle errors
    without raising exceptions to the calling code.
    """
    
    @staticmethod
    async def notify_client_created(
        client_name: str,
        dni_number: str,
        phone: str
    ) -> None:
        """
        Send Telegram notification for new client registration.
        
        Args:
            client_name: Full name of the client
            dni_number: Client's DNI number
            phone: Client's phone number
        
        Returns:
            None (errors are logged but not raised)
        """
        try:
            message = format_client_create_message(
                client_name=client_name,
                dni_number=dni_number,
                phone=phone
            )
            await ClientNotificationHandler._send_notification(message)
            logger.debug("Client creation notification sent for: %s", client_name)
        except Exception as e:
            logger.error(
                "Error sending client creation notification: %s",
                str(e),
                exc_info=True
            )
    
    @staticmethod
    async def notify_client_updated(
        client_name: str,
        dni_number: str
    ) -> None:
        """
        Send Telegram notification for client update.
        
        Args:
            client_name: Full name of the client
            dni_number: Client's DNI number
        
        Returns:
            None (errors are logged but not raised)
        """
        try:
            message = format_client_update_message(
                client_name=client_name,
                dni_number=dni_number
            )
            await ClientNotificationHandler._send_notification(message)
            logger.debug("Client update notification sent for: %s", client_name)
        except Exception as e:
            logger.error(
                "Error sending client update notification: %s",
                str(e),
                exc_info=True
            )
    
    @staticmethod
    async def notify_client_deleted(
        client_name: str,
        dni_number: str
    ) -> None:
        """
        Send Telegram notification for client deletion.
        
        Args:
            client_name: Full name of the client
            dni_number: Client's DNI number
        
        Returns:
            None (errors are logged but not raised)
        """
        try:
            message = format_client_delete_message(
                client_name=client_name,
                dni_number=dni_number
            )
            await ClientNotificationHandler._send_notification(message)
            logger.debug("Client deletion notification sent for: %s", client_name)
        except Exception as e:
            logger.error(
                "Error sending client deletion notification: %s",
                str(e),
                exc_info=True
            )

