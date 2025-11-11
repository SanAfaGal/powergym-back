"""
API dependencies for PowerGym API.

This module provides FastAPI dependencies for authentication and authorization,
including user authentication, role-based access control, and user validation.
"""

from typing import Annotated
import logging

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.schemas.user import User, UserRole
from app.services.user_service import UserService
from app.db.session import get_db
from app.utils.exceptions import UnauthorizedError, ForbiddenError

logger = logging.getLogger(__name__)

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> User:
    """
    Get the current authenticated user from JWT token.

    This dependency extracts the JWT token from the request, decodes it,
    and retrieves the corresponding user from the database.

    Args:
        token: JWT access token from Authorization header
        db: Database session (dependency)

    Returns:
        User schema instance

    Raises:
        UnauthorizedError: If token is invalid, expired, or user not found
    """
    credentials_exception = UnauthorizedError(
        detail="Could not validate credentials"
    )

    try:
        payload = decode_token(token)
        if not payload:
            raise credentials_exception

        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        if username is None or token_type != "access":
            raise credentials_exception

        user = UserService.get_user_by_username(db, username)
        if user is None:
            raise credentials_exception

        return user

    except UnauthorizedError:
        raise
    except Exception as e:
        logger.error("Error validating token: %s", str(e), exc_info=True)
        raise credentials_exception from e


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get the current authenticated and active user.

    This dependency ensures the user is not disabled.

    Args:
        current_user: Authenticated user (dependency)

    Returns:
        Active User schema instance

    Raises:
        UnauthorizedError: If user is disabled
    """
    if current_user.disabled:
        raise UnauthorizedError(detail="Inactive user")
    return current_user


def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Get the current authenticated user with admin role.

    This dependency ensures the user has admin privileges.

    Args:
        current_user: Authenticated active user (dependency)

    Returns:
        Admin User schema instance

    Raises:
        ForbiddenError: If user is not an admin
    """
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenError(
            detail="Not enough permissions. Admin role required."
        )
    return current_user
