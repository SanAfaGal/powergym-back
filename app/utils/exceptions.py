"""
Custom exceptions for PowerGym API.

This module provides custom exception classes that extend FastAPI's HTTPException
for consistent error handling across the application.
"""

from typing import Optional
from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    """Exception raised when a requested resource is not found."""

    def __init__(
        self,
        resource_name: str,
        resource_id: Optional[str] = None,
        detail: Optional[str] = None,
    ) -> None:
        """
        Initialize NotFoundError.

        Args:
            resource_name: Name of the resource type (e.g., "Client", "Subscription")
            resource_id: Optional identifier of the resource
            detail: Optional custom error message
        """
        if detail is None:
            if resource_id:
                detail = f"{resource_name} with id '{resource_id}' not found"
            else:
                detail = f"{resource_name} not found"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ValidationError(HTTPException):
    """Exception raised when validation fails."""

    def __init__(self, detail: str, field: Optional[str] = None) -> None:
        """
        Initialize ValidationError.

        Args:
            detail: Error message describing the validation failure
            field: Optional field name that failed validation
        """
        if field:
            detail = f"Validation error in field '{field}': {detail}"

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class ConflictError(HTTPException):
    """Exception raised when a resource conflict occurs (e.g., duplicate entry)."""

    def __init__(self, detail: str) -> None:
        """
        Initialize ConflictError.

        Args:
            detail: Error message describing the conflict
        """
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class UnauthorizedError(HTTPException):
    """Exception raised when authentication fails."""

    def __init__(self, detail: Optional[str] = None) -> None:
        """
        Initialize UnauthorizedError.

        Args:
            detail: Optional custom error message
        """
        if detail is None:
            detail = "Could not validate credentials"

        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenError(HTTPException):
    """Exception raised when access is forbidden."""

    def __init__(self, detail: Optional[str] = None) -> None:
        """
        Initialize ForbiddenError.

        Args:
            detail: Optional custom error message
        """
        if detail is None:
            detail = "Not enough permissions"

        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class InternalServerError(HTTPException):
    """Exception raised for internal server errors."""

    def __init__(self, detail: Optional[str] = None) -> None:
        """
        Initialize InternalServerError.

        Args:
            detail: Optional custom error message
        """
        if detail is None:
            detail = "Internal server error"

        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )

