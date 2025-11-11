"""
Client validation utilities for PowerGym API.

This module provides reusable validation functions for client-related operations,
including existence checks, uniqueness validation, and relationship verification.
"""

from typing import Optional
from uuid import UUID
import logging

from sqlalchemy.orm import Session

from app.services.client_service import ClientService
from app.services.subscription_service import SubscriptionService
from app.utils.exceptions import NotFoundError, ConflictError
from app.core.constants import ERROR_CLIENT_NOT_FOUND, ERROR_DNI_ALREADY_EXISTS

logger = logging.getLogger(__name__)


class ClientValidator:
    """
    Reusable validator for client-related operations.

    Provides static methods for common validation tasks such as
    checking existence, verifying uniqueness, and validating relationships.
    """

    @staticmethod
    def get_or_404(db: Session, client_id: UUID) -> "Client":
        """
        Retrieve a client or raise 404 error if not found.

        Args:
            db: Database session
            client_id: Client UUID

        Returns:
            Client schema instance

        Raises:
            NotFoundError: If client is not found
        """
        client = ClientService.get_client_by_id(db, client_id)
        if not client:
            raise NotFoundError(
                resource_name="Client", resource_id=str(client_id)
            )
        return client

    @staticmethod
    def verify_subscription_belongs_to_client(
        db: Session,
        subscription_id: UUID,
        client_id: UUID,
    ) -> "Subscription":
        """
        Verify that a subscription belongs to a specific client.

        Args:
            db: Database session
            subscription_id: Subscription UUID
            client_id: Client UUID

        Returns:
            Subscription schema instance

        Raises:
            NotFoundError: If subscription is not found
            ConflictError: If subscription does not belong to client
        """
        subscription = SubscriptionService.get_subscription_by_id(
            db, subscription_id
        )
        if not subscription:
            raise NotFoundError(
                resource_name="Subscription", resource_id=str(subscription_id)
            )

        if subscription.client_id != client_id:
            raise ConflictError(
                detail="The subscription does not belong to this client"
            )

        return subscription

    @staticmethod
    def verify_dni_uniqueness(
        db: Session, dni: str, current_dni: Optional[str] = None
    ) -> None:
        """
        Verify that a DNI number is unique (except for the current client).

        Args:
            db: Database session
            dni: DNI number to validate
            current_dni: Optional current DNI (to exclude from uniqueness check)

        Raises:
            ConflictError: If DNI already exists for another client
        """
        if dni and dni != current_dni:
            existing = ClientService.get_client_by_dni(db, dni)
            if existing:
                raise ConflictError(detail=ERROR_DNI_ALREADY_EXISTS)
