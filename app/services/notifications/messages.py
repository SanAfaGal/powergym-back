"""
Spanish message templates for Telegram notifications.

This module centralizes all Spanish message templates used in Telegram notifications.
Messages are organized by notification type and use format strings for dynamic content.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional


# ============================================================================
# EMOJI MAPPINGS
# ============================================================================

class Emoji:
    """Emoji constants for consistent use across notifications."""
    
    CLIENT = "👤"
    CLIENT_CREATE = "➕"
    CLIENT_UPDATE = "✏️"
    CLIENT_DELETE = "🗑️"
    
    SUBSCRIPTION = "📋"
    SUBSCRIPTION_CREATE = "➕"
    SUBSCRIPTION_UPDATE = "✏️"
    SUBSCRIPTION_CANCEL = "❌"
    SUBSCRIPTION_RENEW = "🔄"
    
    PAYMENT = "💰"
    PAYMENT_CREATE = "➕"
    PAYMENT_UPDATE = "✏️"
    PAYMENT_DELETE = "🗑️"
    
    REWARD = "🎁"
    REWARD_REDEEM = "✅"
    
    INVENTORY = "📦"
    PRODUCT_CREATE = "➕"
    PRODUCT_UPDATE = "✏️"
    PRODUCT_DELETE = "🗑️"
    STOCK_ADD = "📥"
    STOCK_REMOVE = "📤"
    STOCK_SALE = "🛒"
    
    ATTENDANCE = "🏋️"
    CHECK_IN = "✅"


# ============================================================================
# CLIENT NOTIFICATIONS
# ============================================================================

def format_client_create_message(
    client_name: str,
    dni_number: str,
    phone: str
) -> str:
    """
    Format message for client creation notification.
    
    Args:
        client_name: Full name of the client
        dni_number: Client's DNI number
        phone: Client's phone number
    
    Returns:
        Formatted Spanish message
    """
    return (
        f"{Emoji.CLIENT_CREATE} *Cliente Registrado*\n"
        f"Nombre: {client_name}\n"
        f"DNI: {dni_number}\n"
        f"Teléfono: {phone}"
    )


def format_client_update_message(
    client_name: str,
    dni_number: str
) -> str:
    """
    Format message for client update notification.
    
    Args:
        client_name: Full name of the client
        dni_number: Client's DNI number
    
    Returns:
        Formatted Spanish message
    """
    return (
        f"{Emoji.CLIENT_UPDATE} *Cliente Actualizado*\n"
        f"Nombre: {client_name}\n"
        f"DNI: {dni_number}"
    )


def format_client_delete_message(
    client_name: str,
    dni_number: str
) -> str:
    """
    Format message for client deletion notification.
    
    Args:
        client_name: Full name of the client
        dni_number: Client's DNI number
    
    Returns:
        Formatted Spanish message
    """
    return (
        f"{Emoji.CLIENT_DELETE} *Cliente Eliminado*\n"
        f"Nombre: {client_name}\n"
        f"DNI: {dni_number}"
    )


# ============================================================================
# SUBSCRIPTION NOTIFICATIONS
# ============================================================================

def format_subscription_create_message(
    client_name: str,
    plan_name: str,
    start_date: str,
    end_date: str,
    plan_price: Decimal,
    status: str
) -> str:
    """
    Format message for subscription creation notification.
    
    Args:
        client_name: Full name of the client
        plan_name: Name of the subscription plan
        start_date: Subscription start date (formatted string)
        end_date: Subscription end date (formatted string)
        plan_price: Plan price
        status: Subscription status
    
    Returns:
        Formatted Spanish message
    """
    from app.utils.common.formatters import format_currency
    
    price_str = format_currency(plan_price)
    
    # Map status to Spanish display name
    status_map = {
        "pending_payment": "Pago Pendiente",
        "active": "Activa",
        "expired": "Expirada",
        "cancelled": "Cancelada",
        "scheduled": "Programada"
    }
    status_str = status_map.get(status.lower(), status)
    
    return (
        f"{Emoji.SUBSCRIPTION_CREATE} *Nueva Suscripción*\n"
        f"Cliente: {client_name}\n"
        f"Plan: {plan_name}\n"
        f"Inicio: {start_date}\n"
        f"Fin: {end_date}\n"
        f"Precio: {price_str}\n"
        f"Estado: {status_str}"
    )


def format_subscription_update_message(
    client_name: str,
    plan_name: str,
    subscription_id: str
) -> str:
    """
    Format message for subscription update notification.
    
    Args:
        client_name: Full name of the client
        plan_name: Name of the subscription plan
        subscription_id: Subscription UUID
    
    Returns:
        Formatted Spanish message
    """
    return (
        f"{Emoji.SUBSCRIPTION_UPDATE} *Suscripción Actualizada*\n"
        f"Cliente: {client_name}\n"
        f"Plan: {plan_name}\n"
        f"ID: {subscription_id}"
    )


def format_subscription_cancel_message(
    client_name: str,
    plan_name: str,
    cancellation_reason: Optional[str] = None
) -> str:
    """
    Format message for subscription cancellation notification.
    
    Args:
        client_name: Full name of the client
        plan_name: Name of the subscription plan
        cancellation_reason: Optional cancellation reason
    
    Returns:
        Formatted Spanish message
    """
    message = (
        f"{Emoji.SUBSCRIPTION_CANCEL} *Suscripción Cancelada*\n"
        f"Cliente: {client_name}\n"
        f"Plan: {plan_name}"
    )
    
    if cancellation_reason:
        message += f"\nRazón: {cancellation_reason}"
    
    return message


def format_subscription_renew_message(
    client_name: str,
    plan_name: str,
    start_date: str,
    end_date: str
) -> str:
    """
    Format message for subscription renewal notification.
    
    Args:
        client_name: Full name of the client
        plan_name: Name of the subscription plan
        start_date: New subscription start date
        end_date: New subscription end date
    
    Returns:
        Formatted Spanish message
    """
    return (
        f"{Emoji.SUBSCRIPTION_RENEW} *Suscripción Renovada*\n"
        f"Cliente: {client_name}\n"
        f"Plan: {plan_name}\n"
        f"Inicio: {start_date}\n"
        f"Fin: {end_date}"
    )


# ============================================================================
# PAYMENT NOTIFICATIONS
# ============================================================================

def format_payment_create_message(
    client_name: str,
    amount: Decimal,
    payment_method: str,
    plan_name: str,
    remaining_debt: Optional[Decimal] = None
) -> str:
    """
    Format message for payment creation notification.
    
    Args:
        client_name: Full name of the client
        amount: Payment amount
        payment_method: Payment method used
        plan_name: Name of the subscription plan
        remaining_debt: Remaining debt amount (optional)
    
    Returns:
        Formatted Spanish message
    """
    from app.utils.common.formatters import format_currency
    
    amount_str = format_currency(amount)
    debt_str = format_currency(remaining_debt) if remaining_debt is not None else "$0.00"
    
    # Map payment method to Spanish display name
    method_map = {
        "cash": "Efectivo",
        "card": "Tarjeta",
        "transfer": "Transferencia",
        "qr": "QR"
    }
    method_str = method_map.get(payment_method.lower(), payment_method)
    
    return (
        f"{Emoji.PAYMENT_CREATE} *Pago Recibido*\n"
        f"Cliente: {client_name}\n"
        f"Monto: {amount_str}\n"
        f"Método: {method_str}\n"
        f"Suscripción: {plan_name}\n"
        f"Deuda restante: {debt_str}"
    )


def format_payment_update_message(
    client_name: str,
    amount: Decimal,
    payment_id: str
) -> str:
    """
    Format message for payment update notification.
    
    Args:
        client_name: Full name of the client
        amount: Updated payment amount
        payment_id: Payment UUID
    
    Returns:
        Formatted Spanish message
    """
    from app.utils.common.formatters import format_currency
    
    amount_str = format_currency(amount)
    
    return (
        f"{Emoji.PAYMENT_UPDATE} *Pago Actualizado*\n"
        f"Cliente: {client_name}\n"
        f"Monto: {amount_str}\n"
        f"ID: {payment_id}"
    )


def format_payment_delete_message(
    client_name: str,
    amount: Decimal,
    payment_id: str
) -> str:
    """
    Format message for payment deletion notification.
    
    Args:
        client_name: Full name of the client
        amount: Deleted payment amount
        payment_id: Payment UUID
    
    Returns:
        Formatted Spanish message
    """
    from app.utils.common.formatters import format_currency
    
    amount_str = format_currency(amount)
    
    return (
        f"{Emoji.PAYMENT_DELETE} *Pago Eliminado*\n"
        f"Cliente: {client_name}\n"
        f"Monto: {amount_str}\n"
        f"ID: {payment_id}"
    )


# ============================================================================
# REWARD NOTIFICATIONS
# ============================================================================

def format_reward_redeem_message(
    client_name: str,
    discount_percentage: Decimal,
    subscription_plan: str
) -> str:
    """
    Format message for reward redemption notification.
    
    Args:
        client_name: Full name of the client
        discount_percentage: Discount percentage applied
        subscription_plan: Name of the subscription plan where reward was applied
    
    Returns:
        Formatted Spanish message
    """
    return (
        f"{Emoji.REWARD_REDEEM} *Recompensa Canjeada*\n"
        f"Cliente: {client_name}\n"
        f"Descuento: {discount_percentage}%\n"
        f"Plan: {subscription_plan}"
    )


# ============================================================================
# INVENTORY NOTIFICATIONS
# ============================================================================

def format_product_create_message(
    product_name: str,
    price: Decimal,
    initial_stock: Decimal
) -> str:
    """
    Format message for product creation notification.
    
    Args:
        product_name: Name of the product
        price: Product price
        initial_stock: Initial stock quantity
    
    Returns:
        Formatted Spanish message
    """
    from app.utils.common.formatters import format_currency, format_quantity
    
    price_str = format_currency(price)
    stock_str = format_quantity(initial_stock, "unidades")
    
    return (
        f"{Emoji.PRODUCT_CREATE} *Producto Creado*\n"
        f"Producto: {product_name}\n"
        f"Precio: {price_str}\n"
        f"Stock inicial: {stock_str}"
    )


def format_product_update_message(
    product_name: str,
    product_id: str
) -> str:
    """
    Format message for product update notification.
    
    Args:
        product_name: Name of the product
        product_id: Product UUID
    
    Returns:
        Formatted Spanish message
    """
    return (
        f"{Emoji.PRODUCT_UPDATE} *Producto Actualizado*\n"
        f"Producto: {product_name}\n"
        f"ID: {product_id}"
    )


def format_product_delete_message(
    product_name: str,
    product_id: str
) -> str:
    """
    Format message for product deletion notification.
    
    Args:
        product_name: Name of the product
        product_id: Product UUID
    
    Returns:
        Formatted Spanish message
    """
    return (
        f"{Emoji.PRODUCT_DELETE} *Producto Eliminado*\n"
        f"Producto: {product_name}\n"
        f"ID: {product_id}"
    )


def format_stock_add_message(
    product_name: str,
    quantity: Decimal,
    new_stock: Decimal,
    notes: Optional[str] = None
) -> str:
    """
    Format message for stock addition notification.
    
    Args:
        product_name: Name of the product
        quantity: Quantity added
        new_stock: New total stock after addition
        notes: Optional notes about the addition
    
    Returns:
        Formatted Spanish message
    """
    from app.utils.common.formatters import format_quantity
    
    quantity_str = format_quantity(quantity, "unidades")
    stock_str = format_quantity(new_stock, "unidades")
    
    message = (
        f"{Emoji.STOCK_ADD} *Stock Agregado*\n"
        f"Producto: {product_name}\n"
        f"Cantidad agregada: {quantity_str}\n"
        f"Stock total: {stock_str}"
    )
    
    if notes:
        message += f"\nNotas: {notes}"
    
    return message


def format_stock_remove_message(
    product_name: str,
    quantity: Decimal,
    unit_price: Decimal,
    total: Decimal,
    responsible: Optional[str] = None
) -> str:
    """
    Format message for stock removal (sale) notification.
    
    Args:
        product_name: Name of the product
        quantity: Quantity sold/removed
        unit_price: Unit price of the product
        total: Total sale amount
        responsible: Name of the person responsible (optional)
    
    Returns:
        Formatted Spanish message
    """
    from app.utils.common.formatters import format_currency, format_quantity
    
    quantity_str = format_quantity(quantity, "unidades")
    unit_price_str = format_currency(unit_price)
    total_str = format_currency(total)
    
    message = (
        f"{Emoji.STOCK_SALE} *Venta de Producto*\n"
        f"Producto: {product_name}\n"
        f"Cantidad: {quantity_str}\n"
        f"Precio unitario: {unit_price_str}\n"
        f"Total: {total_str}"
    )
    
    if responsible:
        message += f"\nResponsable: {responsible}"
    
    return message


# ============================================================================
# ATTENDANCE NOTIFICATIONS
# ============================================================================

def format_check_in_message(
    client_name: str,
    dni_number: str,
    check_in_time: datetime
) -> str:
    """
    Format message for check-in notification.
    
    Args:
        client_name: Full name of the client
        dni_number: Client's DNI number
        check_in_time: Datetime of the check-in
    
    Returns:
        Formatted Spanish message
    """
    from app.utils.common.formatters import format_time
    
    time_str = format_time(check_in_time)
    
    return (
        f"{Emoji.CHECK_IN} *Check-in*\n"
        f"Cliente: {client_name}\n"
        f"DNI: {dni_number}\n"
        f"Hora: {time_str}"
    )

