"""
Authentication endpoints for PowerGym API.

This module provides REST API endpoints for user authentication,
including login, token refresh, and user registration.
"""

from datetime import timedelta
from typing import Annotated
import logging

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.schemas.token import Token, RefreshTokenRequest
from app.schemas.user import UserCreate, User
from app.services.user_service import UserService
from app.api.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
)
from app.utils.exceptions import (
    UnauthorizedError,
    ConflictError,
    ValidationError,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/register",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account. Only administrators can register new users.",
    responses={
        201: {
            "description": "User successfully registered",
            "content": {
                "application/json": {
                    "example": {
                        "username": "john_doe",
                        "email": "john@example.com",
                        "full_name": "John Doe",
                        "role": "employee",
                        "disabled": False,
                    }
                }
            },
        },
        400: {"description": "Username or email already exists"},
        403: {"description": "Only administrators can register new users"},
    },
)
def register(
    user_data: UserCreate,
    current_user: Annotated[User, Depends(get_current_admin_user)],
    db: Session = Depends(get_db),
) -> User:
    """
    Register a new user account.

    **Required permissions:** Admin only

    Args:
        user_data: User creation data
        current_user: Authenticated admin user (dependency)
        db: Database session (dependency)

    Returns:
        Created User instance

    Raises:
        ConflictError: If username or email already exists
    """
    try:
        existing_user = UserService.get_user_by_username(db, user_data.username)
        if existing_user:
            raise ConflictError(detail="Username already exists")

        existing_email = UserService.get_user_by_email(db, user_data.email)
        if existing_email:
            raise ConflictError(detail="Email already registered")

        new_user = UserService.create_user(db, user_data)
        logger.info("User registered successfully: %s", user_data.username)
        return new_user

    except ConflictError:
        raise
    except Exception as e:
        logger.error(
            "Error registering user '%s': %s", user_data.username, str(e), exc_info=True
        )
        raise


@router.post(
    "/token",
    response_model=Token,
    summary="Login to get access token",
    description="Authenticate user and receive access and refresh tokens.",
    responses={
        200: {
            "description": "Successful login",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        401: {"description": "Incorrect username or password"},
        400: {"description": "Inactive user"},
    },
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    """
    Authenticate user and receive access and refresh tokens.

    Args:
        form_data: OAuth2 password request form with username and password
        db: Database session (dependency)

    Returns:
        Token instance with access_token and refresh_token

    Raises:
        UnauthorizedError: If credentials are invalid
        ValidationError: If user is inactive
    """
    try:
        user = UserService.authenticate_user(
            db, form_data.username, form_data.password
        )
        if not user:
            raise UnauthorizedError(detail="Incorrect username or password")

        if user.disabled:
            raise ValidationError(
                detail="Inactive user", field="disabled"
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user.username, expires_delta=access_token_expires
        )

        refresh_token_expires = timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)
        refresh_token = create_refresh_token(
            subject=user.username, expires_delta=refresh_token_expires
        )

        logger.info("User logged in successfully: %s", form_data.username)
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    except (UnauthorizedError, ValidationError):
        raise
    except Exception as e:
        logger.error("Error during login: %s", str(e), exc_info=True)
        raise UnauthorizedError(detail="Authentication failed") from e


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Get a new access token using a valid refresh token.",
    responses={
        200: {
            "description": "Token refreshed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                    }
                }
            },
        },
        401: {"description": "Invalid or expired refresh token"},
    },
)
def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> Token:
    """
    Refresh an access token using a valid refresh token.

    Args:
        refresh_request: Refresh token request with refresh_token
        db: Database session (dependency)

    Returns:
        Token instance with new access_token

    Raises:
        UnauthorizedError: If refresh token is invalid or expired
    """
    try:
        payload = decode_token(refresh_request.refresh_token)

        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError(detail="Invalid refresh token")

        username = payload.get("sub")
        if not username:
            raise UnauthorizedError(detail="Invalid refresh token")

        user = UserService.get_user_by_username(db, username)
        if not user or user.disabled:
            raise UnauthorizedError(detail="User not found or inactive")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=username, expires_delta=access_token_expires
        )

        logger.info("Token refreshed successfully for user: %s", username)
        return Token(access_token=access_token, token_type="bearer")

    except UnauthorizedError:
        raise
    except Exception as e:
        logger.error("Error refreshing token: %s", str(e), exc_info=True)
        raise UnauthorizedError(detail="Token refresh failed") from e


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout the current authenticated user.",
    responses={
        200: {
            "description": "Successfully logged out",
            "content": {
                "application/json": {
                    "example": {"message": "Successfully logged out"}
                }
            },
        },
        401: {"description": "Not authenticated"},
    },
)
def logout(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """
    Logout the current authenticated user.

    Note: This is a placeholder endpoint. In a production system with token
    blacklisting, you would invalidate the token here.

    Args:
        current_user: Authenticated user (dependency)

    Returns:
        Success message
    """
    logger.info("User logged out: %s", current_user.username)
    return {"message": "Successfully logged out"}


@router.get(
    "/me",
    response_model=User,
    summary="Get current user",
    description="Retrieve the profile of the currently authenticated user.",
    responses={
        200: {
            "description": "Current user profile",
            "content": {
                "application/json": {
                    "example": {
                        "username": "john_doe",
                        "email": "john@example.com",
                        "full_name": "John Doe",
                        "role": "employee",
                        "disabled": False,
                    }
                }
            },
        },
        401: {"description": "Not authenticated"},
    },
)
def get_auth_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Get the profile of the currently authenticated user.

    Args:
        current_user: Authenticated user (dependency)

    Returns:
        User instance
    """
    return current_user
