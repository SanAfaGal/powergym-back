"""
Async Processing Utilities for PowerGym API.

This module provides utilities to safely execute async functions from synchronous code,
which is necessary when calling async notification functions from sync service methods.
"""

import asyncio
import logging
from typing import Coroutine, Any
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Global thread pool executor for background tasks
_executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="async_worker")


def run_async_in_background(coro: Coroutine[Any, Any, None]) -> None:
    """
    Execute an async coroutine in a background thread.
    
    This function safely runs async code from synchronous contexts (like FastAPI
    sync endpoints) by executing the coroutine in a separate thread with its own
    event loop. Errors are logged but not raised.
    
    Args:
        coro: The coroutine to execute (should return None or be fire-and-forget)
        
    Example:
        >>> async def send_notification():
        ...     await NotificationService.send_check_in_notification(...)
        >>> run_async_in_background(send_notification())
    """
    def run_in_thread():
        """Run the coroutine in a new event loop."""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(coro)
            finally:
                loop.close()
        except Exception as e:
            logger.error(
                "Error executing async task in background: %s",
                str(e),
                exc_info=True
            )
    
    # Submit to thread pool executor
    try:
        _executor.submit(run_in_thread)
    except Exception as e:
        logger.error(
            "Error submitting async task to executor: %s",
            str(e),
            exc_info=True
        )


def run_async_sync(coro: Coroutine[Any, Any, Any]) -> Any:
    """
    Execute an async coroutine synchronously by creating a new event loop.
    
    WARNING: This blocks the current thread. Use only when you need to wait
    for the result. For fire-and-forget operations, use run_async_in_background.
    
    Args:
        coro: The coroutine to execute
        
    Returns:
        The result of the coroutine
        
    Example:
        >>> result = run_async_sync(some_async_function())
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    except Exception as e:
        logger.error(
            "Error executing async task synchronously: %s",
            str(e),
            exc_info=True
        )
        raise


def shutdown_executor():
    """
    Shutdown the thread pool executor gracefully.
    
    Should be called during application shutdown.
    """
    _executor.shutdown(wait=True)
    logger.info("Async processing executor shut down")

