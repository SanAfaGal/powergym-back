"""
Timezone utilities for PowerGym API.

This module provides comprehensive timezone handling utilities for the application.
All database operations use UTC, while business logic and user-facing operations
use Colombia timezone (America/Bogota).

Timezone Strategy:
- Database Storage: Always store datetimes in UTC (timezone-aware)
- Date Comparisons: Use Colombia timezone for business logic (e.g., "today", "this week")
- API Responses: Convert UTC datetimes to Colombia timezone before returning
- API Inputs: Accept dates/datetimes, convert to UTC for database storage
- Internal Calculations: Use Colombia timezone for date arithmetic, convert to UTC for queries

Best Practices:
- Never use date.today() or datetime.now() without timezone
- Always use utility functions from this module
- Use get_current_utc_datetime() for UTC timestamps
- Use get_current_colombia_datetime() for Colombia timestamps
- Use get_today_colombia() for date comparisons
- Use convert_to_utc() / convert_to_colombia() for conversions

Example:
    >>> from app.utils.timezone import get_current_colombia_datetime, convert_to_utc
    >>> colombia_now = get_current_colombia_datetime()
    >>> utc_now = convert_to_utc(colombia_now)
"""

from __future__ import annotations

import logging
from datetime import datetime, date, timezone, timedelta
from typing import Union, Optional
from calendar import monthrange

import pytz

# Module-level logger
logger = logging.getLogger(__name__)

# ============================================================================
# Constants
# ============================================================================

COLOMBIA_TIMEZONE: pytz.BaseTzInfo = pytz.timezone("America/Bogota")
UTC_TIMEZONE: timezone = timezone.utc

# Backward compatibility - deprecated, use COLOMBIA_TIMEZONE instead
TIMEZONE: pytz.BaseTzInfo = COLOMBIA_TIMEZONE

# Type aliases for better readability
DateRange = tuple[datetime, datetime]


# ============================================================================
# Custom Exceptions
# ============================================================================

class TimezoneError(Exception):
    """Base exception for timezone-related errors."""
    pass


class TimezoneConversionError(TimezoneError):
    """Raised when datetime conversion fails."""
    pass


class AmbiguousTimezoneError(TimezoneError):
    """Raised when datetime timezone is ambiguous."""
    pass


class InvalidTimezoneError(TimezoneError):
    """Raised when timezone operation is invalid."""
    pass


# ============================================================================
# Current Time Functions
# ============================================================================

def get_current_utc_datetime() -> datetime:
    """
    Get current UTC datetime (timezone-aware).

    Returns:
        datetime: Current datetime in UTC with timezone information.

    Example:
        >>> utc_now = get_current_utc_datetime()
        >>> utc_now.tzinfo
        datetime.timezone.utc
    """
    current_datetime = datetime.now(UTC_TIMEZONE)
    logger.debug("Retrieved current UTC datetime: %s", current_datetime)
    return current_datetime


def get_current_colombia_datetime() -> datetime:
    """
    Get current datetime in Colombia timezone (timezone-aware).

    Returns:
        datetime: Current datetime in Colombia timezone (America/Bogota).

    Example:
        >>> colombia_now = get_current_colombia_datetime()
        >>> colombia_now.tzinfo.zone
        'America/Bogota'
    """
    current_datetime = datetime.now(COLOMBIA_TIMEZONE)
    logger.debug("Retrieved current Colombia datetime: %s", current_datetime)
    return current_datetime


def get_today_colombia() -> date:
    """
    Get today's date in Colombia timezone.

    This function ensures that "today" is determined based on Colombia timezone,
    not the server's local timezone. This is important for date comparisons in
    business logic.

    Returns:
        date: Today's date in Colombia timezone.

    Example:
        >>> today = get_today_colombia()
        >>> isinstance(today, date)
        True
    """
    today_date = get_current_colombia_datetime().date()
    logger.debug("Retrieved today's date in Colombia: %s", today_date)
    return today_date


def get_today_utc() -> date:
    """
    Get today's date in UTC.

    Returns:
        date: Today's date in UTC.

    Example:
        >>> today_utc = get_today_utc()
        >>> isinstance(today_utc, date)
        True
    """
    today_date = get_current_utc_datetime().date()
    logger.debug("Retrieved today's date in UTC: %s", today_date)
    return today_date


# ============================================================================
# Conversion Functions
# ============================================================================

def convert_to_utc(datetime_value: datetime) -> datetime:
    """
    Convert any datetime to UTC.

    Handles naive datetimes (assumes UTC), Colombia timezone, or already UTC datetimes.
    Raises exception if conversion is ambiguous or fails.

    Args:
        datetime_value: Datetime to convert (can be naive, UTC, or Colombia timezone).

    Returns:
        datetime: Datetime in UTC (timezone-aware).

    Raises:
        AmbiguousTimezoneError: If datetime is naive and cannot be safely converted.
        TimezoneConversionError: If conversion fails.

    Example:
        >>> naive_dt = datetime(2024, 1, 15, 12, 0, 0)
        >>> utc_dt = convert_to_utc(naive_dt)
        >>> utc_dt.tzinfo
        datetime.timezone.utc
    """
    if datetime_value.tzinfo is None:
        logger.warning(
            "Converting naive datetime to UTC (assuming UTC): %s",
            datetime_value
        )
        return datetime_value.replace(tzinfo=UTC_TIMEZONE)

    if datetime_value.tzinfo == UTC_TIMEZONE:
        logger.debug("Datetime already in UTC: %s", datetime_value)
        return datetime_value

    try:
        converted_datetime = datetime_value.astimezone(UTC_TIMEZONE)
        logger.debug(
            "Converted datetime to UTC: %s -> %s",
            datetime_value,
            converted_datetime
        )
        return converted_datetime
    except Exception as e:
        error_msg = f"Failed to convert datetime to UTC: {datetime_value}"
        logger.error("%s - Error: %s", error_msg, str(e), exc_info=True)
        raise TimezoneConversionError(error_msg) from e


def convert_to_colombia(datetime_value: datetime) -> datetime:
    """
    Convert any datetime to Colombia timezone.

    Handles naive datetimes (assumes UTC), UTC, or already Colombia timezone datetimes.
    Raises exception if conversion fails.

    Args:
        datetime_value: Datetime to convert (can be naive, UTC, or Colombia timezone).

    Returns:
        datetime: Datetime in Colombia timezone (timezone-aware).

    Raises:
        TimezoneConversionError: If conversion fails.

    Example:
        >>> utc_dt = datetime(2024, 1, 15, 17, 0, 0, tzinfo=timezone.utc)
        >>> colombia_dt = convert_to_colombia(utc_dt)
        >>> colombia_dt.tzinfo.zone
        'America/Bogota'
    """
    if datetime_value.tzinfo is None:
        logger.warning(
            "Converting naive datetime to Colombia (assuming UTC): %s",
            datetime_value
        )
        # Assume naive datetime is in UTC
        datetime_value = datetime_value.replace(tzinfo=UTC_TIMEZONE)

    if datetime_value.tzinfo == COLOMBIA_TIMEZONE or (
        hasattr(datetime_value.tzinfo, 'zone') and
        datetime_value.tzinfo.zone == COLOMBIA_TIMEZONE.zone
    ):
        logger.debug("Datetime already in Colombia timezone: %s", datetime_value)
        return datetime_value

    try:
        converted_datetime = datetime_value.astimezone(COLOMBIA_TIMEZONE)
        logger.debug(
            "Converted datetime to Colombia: %s -> %s",
            datetime_value,
            converted_datetime
        )
        return converted_datetime
    except Exception as e:
        error_msg = f"Failed to convert datetime to Colombia: {datetime_value}"
        logger.error("%s - Error: %s", error_msg, str(e), exc_info=True)
        raise TimezoneConversionError(error_msg) from e


def to_local(utc_datetime: datetime) -> datetime:
    """
    Convert UTC datetime to local (Colombia) timezone.

    This function is maintained for backward compatibility.
    New code should use convert_to_colombia() instead.

    Args:
        utc_datetime: UTC datetime to convert.

    Returns:
        datetime: Datetime in Colombia timezone.

    Deprecated:
        Use convert_to_colombia() instead.
    """
    logger.warning(
        "to_local() is deprecated. Use convert_to_colombia() instead."
    )
    return convert_to_colombia(utc_datetime)


# ============================================================================
# Date Range Functions
# ============================================================================

def get_day_range_utc(target_date: Union[date, datetime]) -> DateRange:
    """
    Convert a local date to UTC day range (start and end of day).

    Takes a date (or datetime) in Colombia timezone and returns the UTC datetime
    range representing the start (00:00:00) and end (23:59:59.999999) of that day.

    Args:
        target_date: Date or datetime in Colombia timezone. If datetime, only
                     the date part is used.

    Returns:
        tuple[datetime, datetime]: Start and end of day in UTC (timezone-aware).

    Raises:
        InvalidTimezoneError: If date cannot be processed.

    Example:
        >>> from datetime import date
        >>> start, end = get_day_range_utc(date(2024, 1, 15))
        >>> start.tzinfo
        datetime.timezone.utc
        >>> end.tzinfo
        datetime.timezone.utc
    """
    try:
        # Extract date if datetime is provided
        if isinstance(target_date, datetime):
            target_date_value = target_date.date()
        else:
            target_date_value = target_date

        # Create start of day in Colombia timezone
        start_of_day_colombia = COLOMBIA_TIMEZONE.localize(
            datetime.combine(target_date_value, datetime.min.time())
        )

        # Create end of day in Colombia timezone
        end_of_day_colombia = COLOMBIA_TIMEZONE.localize(
            datetime.combine(target_date_value, datetime.max.time())
        )

        # Convert to UTC
        start_of_day_utc = start_of_day_colombia.astimezone(UTC_TIMEZONE)
        end_of_day_utc = end_of_day_colombia.astimezone(UTC_TIMEZONE)

        logger.debug(
            "Calculated UTC day range for %s: %s to %s",
            target_date_value,
            start_of_day_utc,
            end_of_day_utc
        )

        return start_of_day_utc, end_of_day_utc

    except Exception as e:
        error_msg = f"Failed to calculate UTC day range for date: {target_date}"
        logger.error("%s - Error: %s", error_msg, str(e), exc_info=True)
        raise InvalidTimezoneError(error_msg) from e


def get_date_range_utc(local_date: Union[date, datetime]) -> DateRange:
    """
    Convert a local date to UTC range (backward compatibility).

    This function is maintained for backward compatibility.
    New code should use get_day_range_utc() instead.

    Args:
        local_date: Date or datetime in Colombia timezone.

    Returns:
        tuple[datetime, datetime]: Start and end of day in UTC.

    Deprecated:
        Use get_day_range_utc() instead.
    """
    logger.debug("get_date_range_utc() called (use get_day_range_utc() instead)")
    return get_day_range_utc(local_date)


def get_period_range_utc(start_date: date, end_date: date) -> DateRange:
    """
    Get UTC range for a date period.

    Converts start and end dates (in Colombia timezone) to UTC datetime range.
    Start date begins at 00:00:00, end date ends at 23:59:59.999999.

    Args:
        start_date: Start date of the period (in Colombia timezone).
        end_date: End date of the period (in Colombia timezone).

    Returns:
        tuple[datetime, datetime]: Start and end of period in UTC (timezone-aware).

    Raises:
        ValueError: If start_date > end_date.

    Example:
        >>> from datetime import date
        >>> start, end = get_period_range_utc(date(2024, 1, 1), date(2024, 1, 31))
        >>> start < end
        True
    """
    if start_date > end_date:
        error_msg = (
            f"Invalid date range: start_date ({start_date}) > end_date ({end_date})"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    start_datetime_utc, _ = get_day_range_utc(start_date)
    _, end_datetime_utc = get_day_range_utc(end_date)

    logger.debug(
        "Calculated UTC period range: %s to %s",
        start_datetime_utc,
        end_datetime_utc
    )

    return start_datetime_utc, end_datetime_utc


def get_week_range_utc(reference_date: Optional[date] = None) -> DateRange:
    """
    Get current week range in UTC (Monday to Sunday).

    Args:
        reference_date: Reference date for week calculation. If None, uses today
                        in Colombia timezone. Defaults to None.

    Returns:
        tuple[datetime, datetime]: Start (Monday) and end (Sunday) of week in UTC.

    Example:
        >>> start, end = get_week_range_utc()
        >>> start.weekday() == 0  # Monday
        True
    """
    if reference_date is None:
        reference_date = get_today_colombia()

    # Calculate Monday of the week
    days_since_monday = reference_date.weekday()
    week_start_date = reference_date - timedelta(days=days_since_monday)
    week_end_date = week_start_date + timedelta(days=6)

    start_datetime_utc, _ = get_day_range_utc(week_start_date)
    _, end_datetime_utc = get_day_range_utc(week_end_date)

    logger.debug(
        "Calculated UTC week range: %s to %s",
        start_datetime_utc,
        end_datetime_utc
    )

    return start_datetime_utc, end_datetime_utc


def get_month_range_utc(reference_date: Optional[date] = None) -> DateRange:
    """
    Get current month range in UTC.

    Args:
        reference_date: Reference date for month calculation. If None, uses today
                        in Colombia timezone. Defaults to None.

    Returns:
        tuple[datetime, datetime]: Start (1st) and end (last day) of month in UTC.

    Example:
        >>> start, end = get_month_range_utc(date(2024, 2, 15))
        >>> start.day == 1
        True
    """
    if reference_date is None:
        reference_date = get_today_colombia()

    month_start_date = reference_date.replace(day=1)
    last_day = monthrange(reference_date.year, reference_date.month)[1]
    month_end_date = reference_date.replace(day=last_day)

    start_datetime_utc, _ = get_day_range_utc(month_start_date)
    _, end_datetime_utc = get_day_range_utc(month_end_date)

    logger.debug(
        "Calculated UTC month range: %s to %s",
        start_datetime_utc,
        end_datetime_utc
    )

    return start_datetime_utc, end_datetime_utc


# ============================================================================
# Time Calculation Helpers
# ============================================================================

def get_datetime_hours_ago(
    hours: int,
    reference_datetime: Optional[datetime] = None
) -> datetime:
    """
    Get datetime N hours ago in Colombia timezone, converted to UTC.

    Args:
        hours: Number of hours to go back (must be >= 0).
        reference_datetime: Reference datetime. If None, uses current Colombia
                           datetime. Defaults to None.

    Returns:
        datetime: Datetime N hours ago in UTC (timezone-aware).

    Raises:
        ValueError: If hours < 0.

    Example:
        >>> hours_ago = get_datetime_hours_ago(24)
        >>> isinstance(hours_ago, datetime)
        True
    """
    if hours < 0:
        error_msg = f"Hours must be >= 0, got: {hours}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if reference_datetime is None:
        reference_datetime = get_current_colombia_datetime()
    else:
        # Ensure reference is in Colombia timezone
        reference_datetime = convert_to_colombia(reference_datetime)

    hours_ago_colombia = reference_datetime - timedelta(hours=hours)
    hours_ago_utc = convert_to_utc(hours_ago_colombia)

    logger.debug(
        "Calculated datetime %d hours ago: %s (UTC)",
        hours,
        hours_ago_utc
    )

    return hours_ago_utc


def get_datetime_days_ago(
    days: int,
    reference_date: Optional[date] = None
) -> datetime:
    """
    Get datetime N days ago in Colombia timezone, converted to UTC.

    Args:
        days: Number of days to go back (must be >= 0).
        reference_date: Reference date. If None, uses today in Colombia timezone.
                       Defaults to None.

    Returns:
        datetime: Start of day N days ago in UTC (timezone-aware).

    Raises:
        ValueError: If days < 0.

    Example:
        >>> days_ago = get_datetime_days_ago(7)
        >>> isinstance(days_ago, datetime)
        True
    """
    if days < 0:
        error_msg = f"Days must be >= 0, got: {days}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if reference_date is None:
        reference_date = get_today_colombia()

    days_ago_date = reference_date - timedelta(days=days)
    start_of_day_utc, _ = get_day_range_utc(days_ago_date)

    logger.debug(
        "Calculated datetime %d days ago: %s (UTC)",
        days,
        start_of_day_utc
    )

    return start_of_day_utc


# ============================================================================
# Validation/Helper Functions
# ============================================================================

def ensure_utc_datetime(datetime_value: datetime) -> datetime:
    """
    Ensure datetime is UTC (convert if needed, raise if ambiguous).

    Args:
        datetime_value: Datetime to ensure is UTC.

    Returns:
        datetime: Datetime in UTC (timezone-aware).

    Raises:
        AmbiguousTimezoneError: If datetime is naive and cannot be safely converted.

    Example:
        >>> dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        >>> ensure_utc_datetime(dt)
        datetime.datetime(2024, 1, 15, 12, 0, tzinfo=datetime.timezone.utc)
    """
    if datetime_value.tzinfo is None:
        error_msg = (
            f"Cannot ensure UTC for naive datetime: {datetime_value}. "
            "Use convert_to_utc() to explicitly convert."
        )
        logger.error(error_msg)
        raise AmbiguousTimezoneError(error_msg)

    if datetime_value.tzinfo != UTC_TIMEZONE:
        logger.warning(
            "Converting datetime to UTC: %s -> UTC",
            datetime_value
        )
        return convert_to_utc(datetime_value)

    return datetime_value


def ensure_colombia_datetime(datetime_value: datetime) -> datetime:
    """
    Ensure datetime is in Colombia timezone.

    Args:
        datetime_value: Datetime to ensure is in Colombia timezone.

    Returns:
        datetime: Datetime in Colombia timezone (timezone-aware).

    Raises:
        TimezoneConversionError: If conversion fails.

    Example:
        >>> dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        >>> ensure_colombia_datetime(dt)
        datetime.datetime(2024, 1, 15, 7, 0, tzinfo=<DstTzInfo 'America/Bogota'...>)
    """
    if datetime_value.tzinfo is None:
        error_msg = (
            f"Cannot ensure Colombia timezone for naive datetime: {datetime_value}. "
            "Use convert_to_colombia() to explicitly convert."
        )
        logger.error(error_msg)
        raise AmbiguousTimezoneError(error_msg)

    if datetime_value.tzinfo != COLOMBIA_TIMEZONE and (
        not hasattr(datetime_value.tzinfo, 'zone') or
        datetime_value.tzinfo.zone != COLOMBIA_TIMEZONE.zone
    ):
        logger.warning(
            "Converting datetime to Colombia timezone: %s -> Colombia",
            datetime_value
        )
        return convert_to_colombia(datetime_value)

    return datetime_value


def is_naive_datetime(datetime_value: datetime) -> bool:
    """
    Check if datetime is timezone-naive.

    Args:
        datetime_value: Datetime to check.

    Returns:
        bool: True if datetime is naive (no timezone info), False otherwise.

    Example:
        >>> is_naive_datetime(datetime.now())
        True
        >>> is_naive_datetime(datetime.now(timezone.utc))
        False
    """
    return datetime_value.tzinfo is None
