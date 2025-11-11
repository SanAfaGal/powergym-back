"""
Response helpers for PowerGym API.

This module provides utility functions for creating consistent API responses.
"""

from typing import Any, Optional
from fastapi import status
from fastapi.responses import JSONResponse


def success_response(
    data: Any,
    message: Optional[str] = None,
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    """
    Create a standardized success response.

    Args:
        data: Response data
        message: Optional success message
        status_code: HTTP status code (default: 200)

    Returns:
        JSONResponse with standardized format
    """
    content = {
        "success": True,
        "data": data,
    }
    if message:
        content["message"] = message

    return JSONResponse(status_code=status_code, content=content)


def error_response(
    error: str,
    detail: Optional[str] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    request_id: Optional[str] = None,
) -> JSONResponse:
    """
    Create a standardized error response.

    Args:
        error: Error message
        detail: Optional detailed error information
        status_code: HTTP status code (default: 400)
        request_id: Optional request ID for tracing

    Returns:
        JSONResponse with standardized error format
    """
    content = {
        "success": False,
        "error": error,
        "status_code": status_code,
    }
    if detail:
        content["detail"] = detail
    if request_id:
        content["request_id"] = request_id

    return JSONResponse(status_code=status_code, content=content)

