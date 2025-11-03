"""
Telegram Client for PowerGym API.

This module provides functionality to send messages to Telegram chats via the Bot API.
It handles authentication, error handling, and logging for all Telegram operations.
"""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"
TELEGRAM_API_TIMEOUT = 10.0


async def send_telegram_message(
    chat_id: str,
    message: str,
    parse_mode: str = "Markdown"
) -> bool:
    """
    Send a message to a Telegram chat via Bot API.

    Args:
        chat_id: Telegram chat ID (can be a group ID or user ID)
        message: Message text (supports Markdown formatting)
        parse_mode: Parse mode for formatting ("Markdown" or "HTML", default: "Markdown")

    Returns:
        True if message was sent successfully, False otherwise

    Raises:
        Exception: If Telegram API request fails (logged but not re-raised)

    Example:
        >>> await send_telegram_message("123456789", "Hello, World!")
        True
    """
    # Check if Telegram is enabled
    if not settings.TELEGRAM_ENABLED:
        logger.debug("Telegram notifications are disabled")
        return False

    # Validate required configuration
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN is not configured")
        return False

    if not chat_id:
        logger.warning("Telegram chat_id is not provided")
        return False

    if not message:
        logger.warning("Empty message provided to Telegram")
        return False

    url = TELEGRAM_API_URL.format(token=settings.TELEGRAM_BOT_TOKEN)

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode,
    }

    try:
        async with httpx.AsyncClient(timeout=TELEGRAM_API_TIMEOUT) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                logger.debug("Telegram message sent successfully to chat %s", chat_id)
                return True
            else:
                error_description = result.get("description", "Unknown error")
                error_code = result.get("error_code", "N/A")
                logger.error(
                    "Telegram API error: Code %s - %s",
                    error_code,
                    error_description
                )
                return False

    except httpx.TimeoutException:
        logger.error("Telegram API request timeout after %s seconds", TELEGRAM_API_TIMEOUT)
        return False
    except httpx.HTTPStatusError as e:
        # Try to get error details from response
        try:
            error_data = e.response.json()
            error_description = error_data.get("description", e.response.text)
            logger.error(
                "Telegram API HTTP error: %s - %s",
                e.response.status_code,
                error_description
            )
        except:
            logger.error(
                "Telegram API HTTP error: %s - %s",
                e.response.status_code,
                e.response.text
            )
        return False
    except httpx.RequestError as e:
        logger.error("Telegram API request error: %s", str(e))
        return False
    except Exception as e:
        logger.error(
            "Unexpected error sending Telegram message: %s",
            str(e),
            exc_info=True
        )
        return False


async def send_telegram_message_html(
    chat_id: str,
    message: str
) -> bool:
    """
    Send a message to Telegram using HTML parse mode.

    Args:
        chat_id: Telegram chat ID
        message: Message text with HTML formatting

    Returns:
        True if message was sent successfully, False otherwise

    Example:
        >>> await send_telegram_message_html("123456789", "<b>Bold</b> text")
        True
    """
    return await send_telegram_message(chat_id, message, parse_mode="HTML")
