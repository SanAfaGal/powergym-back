"""
Common formatting utilities for PowerGym API.

This module provides reusable formatting functions for currency, names, dates,
and other common data types used across the application.
"""

from decimal import Decimal
from typing import Optional
from datetime import datetime


def format_currency(amount: Decimal, currency_symbol: str = "$") -> str:
    """
    Format a decimal amount as currency with Colombian format (thousands separator: comma).

    Args:
        amount: The decimal amount to format
        currency_symbol: Currency symbol to use (default: "$")

    Returns:
        Formatted currency string (e.g., "$1.234,56")

    Example:
        >>> format_currency(Decimal("1234.56"))
        "$1.234,56"
    """
    return f"{currency_symbol}{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_client_name(
    first_name: str,
    last_name: str,
    middle_name: Optional[str] = None,
    second_last_name: Optional[str] = None
) -> str:
    """
    Format a client's full name from individual components.

    Args:
        first_name: Client's first name (required)
        last_name: Client's last name (required)
        middle_name: Client's middle name (optional)
        second_last_name: Client's second last name (optional)

    Returns:
        Formatted full name string

    Example:
        >>> format_client_name("Juan", "García", "Carlos", "López")
        "Juan Carlos García López"
    """
    parts = [first_name]
    if middle_name:
        parts.append(middle_name)
    parts.append(last_name)
    if second_last_name:
        parts.append(second_last_name)
    return " ".join(parts)


def format_time(dt: datetime, format_str: str = "%H:%M:%S") -> str:
    """
    Format a datetime object to time string.

    Args:
        dt: Datetime object to format
        format_str: Format string (default: "%H:%M:%S")

    Returns:
        Formatted time string

    Example:
        >>> format_time(datetime(2024, 1, 15, 14, 30, 0))
        "14:30:00"
    """
    return dt.strftime(format_str)


def format_quantity(quantity: Decimal, unit: str = "units") -> str:
    """
    Format a quantity with appropriate unit formatting.

    Args:
        quantity: The quantity to format
        unit: Unit name (default: "units")

    Returns:
        Formatted quantity string

    Example:
        >>> format_quantity(Decimal("5"), "items")
        "5 items"
        >>> format_quantity(Decimal("5.5"), "items")
        "5.5 items"
    """
    if quantity == int(quantity):
        return f"{int(quantity)} {unit}"
    return f"{quantity} {unit}"

