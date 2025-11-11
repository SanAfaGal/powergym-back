"""
Client endpoints for PowerGym API.

This module provides REST API endpoints for client management operations.
"""

from typing import List
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.schemas.client import Client, ClientCreate, ClientUpdate, ClientDashboard
from app.schemas.user import User
from app.services.client_service import ClientService
from app.api.dependencies import get_current_active_user
from app.db.session import get_db
from app.utils.client.validators import ClientValidator
from app.utils.exceptions import NotFoundError, InternalServerError
from app.core.constants import (
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    DEFAULT_SEARCH_LIMIT,
    ERROR_CLIENT_NOT_FOUND,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/clients", tags=["clients"])


@router.post(
    "/",
    response_model=Client,
    status_code=status.HTTP_201_CREATED,
    summary="Create new client",
    description="Register a new client in the gym system",
)
def create_client(
    client_data: ClientCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Client:
    """
    Create a new client.

    Args:
        client_data: Client creation data
        current_user: Authenticated user (dependency)
        db: Database session (dependency)

    Returns:
        Created Client instance

    Raises:
        HTTPException: If validation fails or creation error occurs
    """
    try:
        # Validate DNI uniqueness
        ClientValidator.verify_dni_uniqueness(db, client_data.dni_number)

        client = ClientService.create_client(db, client_data)
        if not client:
            raise InternalServerError(detail="Failed to create client")

        logger.info("Client created successfully: %s", client.id)
        return client

    except Exception as e:
        logger.error("Error creating client: %s", str(e), exc_info=True)
        raise


@router.get(
    "/",
    response_model=List[Client],
    summary="List all clients",
    description="Get a paginated list of clients with optional filters",
)
def list_clients(
    is_active: bool | None = Query(
        None, description="Filter by active/inactive status"
    ),
    search: str | None = Query(
        None, min_length=1, description="Search by name, DNI, email or phone"
    ),
    limit: int = Query(
        DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Maximum results"
    ),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[Client]:
    """
    List all clients with optional filters.

    Args:
        is_active: Optional filter by active status
        search: Optional search term for name, DNI, or phone
        limit: Maximum number of results (default: 100, max: 500)
        offset: Number of results to skip
        current_user: Authenticated user (dependency)
        db: Database session (dependency)

    Returns:
        List of Client instances
    """
    try:
        if search:
            return ClientService.search_clients(db, search, limit)

        return ClientService.list_clients(db, is_active, limit, offset)

    except Exception as e:
        logger.error("Error listing clients: %s", str(e), exc_info=True)
        raise


@router.get(
    "/dni/{dni_number}",
    response_model=Client,
    summary="Get client by DNI",
    description="Retrieve a client using their document number (useful for check-in)",
)
def get_client_by_dni(
    dni_number: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Client:
    """
    Get client by DNI - useful for check-in operations.

    Args:
        dni_number: Client's document number
        current_user: Authenticated user (dependency)
        db: Database session (dependency)

    Returns:
        Client instance

    Raises:
        NotFoundError: If client is not found
    """
    try:
        client = ClientService.get_client_by_dni(db, dni_number)
        if not client:
            raise NotFoundError(resource_name="Client", resource_id=dni_number)

        return client

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(
            "Error retrieving client by DNI '%s': %s", dni_number, str(e), exc_info=True
        )
        raise InternalServerError(detail="Failed to retrieve client") from e


@router.get(
    "/{client_id}",
    response_model=Client,
    summary="Get client by ID",
    description="Retrieve detailed information of a specific client",
)
def get_client(
    client_id: UUID,
    include_biometrics: bool = Query(
        True, description="Include biometric information in response"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Client:
    """
    Get client by ID.

    Args:
        client_id: Client UUID
        include_biometrics: Whether to include biometric data
        current_user: Authenticated user (dependency)
        db: Database session (dependency)

    Returns:
        Client instance

    Raises:
        NotFoundError: If client is not found
    """
    try:
        client = ClientService.get_client_by_id(db, client_id, include_biometrics)
        if not client:
            raise NotFoundError(resource_name="Client", resource_id=str(client_id))

        return client

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(
            "Error retrieving client %s: %s", client_id, str(e), exc_info=True
        )
        raise InternalServerError(detail="Failed to retrieve client") from e


@router.put(
    "/{client_id}",
    response_model=Client,
    summary="Update client",
    description="Update information of an existing client",
)
def update_client(
    client_id: UUID,
    client_update: ClientUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Client:
    """
    Update client information.

    Args:
        client_id: Client UUID to update
        client_update: Client update data
        current_user: Authenticated user (dependency)
        db: Database session (dependency)

    Returns:
        Updated Client instance

    Raises:
        NotFoundError: If client is not found
        InternalServerError: If update fails
    """
    try:
        # Verify client exists
        existing_client = ClientValidator.get_or_404(db, client_id)

        # Validate DNI uniqueness if DNI is being updated
        if client_update.dni_number and client_update.dni_number != existing_client.dni_number:
            ClientValidator.verify_dni_uniqueness(
                db, client_update.dni_number, existing_client.dni_number
            )

        updated = ClientService.update_client(db, client_id, client_update)
        if not updated:
            raise InternalServerError(detail="Failed to update client")

        logger.info("Client updated successfully: %s", client_id)
        return updated

    except NotFoundError:
        raise
    except Exception as e:
        logger.error("Error updating client %s: %s", client_id, str(e), exc_info=True)
        raise


@router.patch(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate client",
    description="Deactivate a client (soft delete). The client can be reactivated",
)
def deactivate_client(
    client_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Deactivate a client (soft delete).

    Args:
        client_id: Client UUID to deactivate
        current_user: Authenticated user (dependency)
        db: Database session (dependency)

    Raises:
        NotFoundError: If client is not found
        InternalServerError: If deactivation fails
    """
    try:
        # Verify client exists
        ClientValidator.get_or_404(db, client_id)

        if not ClientService.delete_client(db, client_id):
            raise InternalServerError(detail="Failed to deactivate client")

        logger.info("Client deactivated successfully: %s", client_id)

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(
            "Error deactivating client %s: %s", client_id, str(e), exc_info=True
        )
        raise


@router.get(
    "/{client_id}/dashboard",
    response_model=ClientDashboard,
    summary="Get client dashboard",
    description="Get summarized client information including current subscription and statistics",
)
def get_client_dashboard(
    client_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> ClientDashboard:
    """
    Get client dashboard with comprehensive information.

    Args:
        client_id: Client UUID
        current_user: Authenticated user (dependency)
        db: Database session (dependency)

    Returns:
        ClientDashboard instance with aggregated data

    Raises:
        NotFoundError: If client is not found
    """
    try:
        dashboard = ClientService.get_client_dashboard(db, client_id)
        if not dashboard:
            raise NotFoundError(resource_name="Client", resource_id=str(client_id))

        return dashboard

    except NotFoundError:
        raise
    except Exception as e:
        logger.error(
            "Error retrieving client dashboard for %s: %s",
            client_id,
            str(e),
            exc_info=True,
        )
        raise InternalServerError(detail="Failed to retrieve client dashboard") from e
