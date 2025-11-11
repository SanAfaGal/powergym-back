"""
Inventory notification handler for PowerGym API.

This module handles all Telegram notifications related to inventory operations:
- Product creation
- Product updates
- Product deletion
- Stock addition
- Stock removal (sales)
"""

import logging
from decimal import Decimal
from typing import Optional

from app.services.notifications.handlers.base_handler import BaseNotificationHandler
from app.services.notifications.messages import (
    format_product_create_message,
    format_product_delete_message,
    format_product_update_message,
    format_stock_add_message,
    format_stock_remove_message,
)

logger = logging.getLogger(__name__)


class InventoryNotificationHandler(BaseNotificationHandler):
    """
    Handler for inventory-related Telegram notifications.
    
    All methods are async and will gracefully handle errors
    without raising exceptions to the calling code.
    """
    
    @staticmethod
    async def notify_product_created(
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
        try:
            message = format_product_create_message(
                product_name=product_name,
                price=price,
                initial_stock=initial_stock
            )
            await InventoryNotificationHandler._send_notification(message)
            logger.debug("Product creation notification sent for product: %s", product_name)
        except Exception as e:
            logger.error(
                "Error sending product creation notification: %s",
                str(e),
                exc_info=True
            )
    
    @staticmethod
    async def notify_product_updated(
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
        try:
            message = format_product_update_message(
                product_name=product_name,
                product_id=product_id
            )
            await InventoryNotificationHandler._send_notification(message)
            logger.debug("Product update notification sent for product: %s", product_id)
        except Exception as e:
            logger.error(
                "Error sending product update notification: %s",
                str(e),
                exc_info=True
            )
    
    @staticmethod
    async def notify_product_deleted(
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
        try:
            message = format_product_delete_message(
                product_name=product_name,
                product_id=product_id
            )
            await InventoryNotificationHandler._send_notification(message)
            logger.debug("Product deletion notification sent for product: %s", product_id)
        except Exception as e:
            logger.error(
                "Error sending product deletion notification: %s",
                str(e),
                exc_info=True
            )
    
    @staticmethod
    async def notify_stock_added(
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
        try:
            message = format_stock_add_message(
                product_name=product_name,
                quantity=quantity,
                new_stock=new_stock,
                notes=notes
            )
            await InventoryNotificationHandler._send_notification(message)
            logger.debug("Stock addition notification sent for product: %s", product_name)
        except Exception as e:
            logger.error(
                "Error sending stock addition notification: %s",
                str(e),
                exc_info=True
            )
    
    @staticmethod
    async def notify_stock_removed(
        product_name: str,
        quantity: Decimal,
        unit_price: Decimal,
        total: Decimal,
        responsible: Optional[str] = None
    ) -> None:
        """
        Send Telegram notification for stock removal (sale).
        
        Args:
            product_name: Name of the product
            quantity: Quantity sold/removed
            unit_price: Unit price of the product
            total: Total sale amount
            responsible: Name of the person responsible (optional)
        
        Returns:
            None (errors are logged but not raised)
        """
        try:
            message = format_stock_remove_message(
                product_name=product_name,
                quantity=quantity,
                unit_price=unit_price,
                total=total,
                responsible=responsible
            )
            await InventoryNotificationHandler._send_notification(message)
            logger.debug("Stock removal notification sent for product: %s", product_name)
        except Exception as e:
            logger.error(
                "Error sending stock removal notification: %s",
                str(e),
                exc_info=True
            )

