"""
Client service for PowerGym API.

This module provides business logic for client management operations,
including CRUD operations, search, and dashboard data aggregation.
"""

from typing import List, Optional
from uuid import UUID
import base64
import logging

from sqlalchemy.orm import Session

from app.schemas.client import (
    Client,
    ClientCreate,
    ClientUpdate,
    ClientDashboard,
    ClientBasicInfo,
    BiometricInfo,
    SubscriptionInfo,
    ClientStats,
)
from app.repositories.client_repository import ClientRepository
from app.db.models import DocumentTypeEnum, GenderTypeEnum, BiometricTypeEnum
from app.core.encryption import get_encryption_service
from app.services.notification_service import NotificationService
from app.core.async_processing import run_async_in_background
from app.utils.mappers import (
    model_to_client_schema,
    models_to_client_schemas,
    document_type_schema_to_enum,
    gender_type_schema_to_enum,
)
from app.utils.exceptions import NotFoundError, InternalServerError
from app.core.constants import ERROR_CLIENT_NOT_FOUND, ERROR_INTERNAL_SERVER

logger = logging.getLogger(__name__)


class ClientService:
    """
    Service for client-related business logic.

    This service handles all client operations including creation, updates,
    retrieval, and dashboard data aggregation. It uses the repository pattern
    for data access and mappers for model-to-schema conversion.
    """

    @staticmethod
    def create_client(db: Session, client_data: ClientCreate) -> Client:
        """
        Create a new client in the system.

        Args:
            db: Database session
            client_data: Client creation data

        Returns:
            Created Client schema instance

        Raises:
            InternalServerError: If client creation fails
        """
        try:
            dni_type_enum = document_type_schema_to_enum(client_data.dni_type)
            gender_enum = gender_type_schema_to_enum(client_data.gender)

            client_model = ClientRepository.create(
                db=db,
                dni_type=dni_type_enum,
                dni_number=client_data.dni_number,
                first_name=client_data.first_name,
                middle_name=client_data.middle_name,
                last_name=client_data.last_name,
                second_last_name=client_data.second_last_name,
                phone=client_data.phone,
                alternative_phone=client_data.alternative_phone,
                birth_date=client_data.birth_date,
                gender=gender_enum,
                address=client_data.address,
            )

            # Send Telegram notification in background (non-blocking)
            try:
                run_async_in_background(
                    NotificationService.send_client_registration_notification(
                        first_name=client_data.first_name,
                        middle_name=client_data.middle_name,
                        last_name=client_data.last_name,
                        second_last_name=client_data.second_last_name,
                        dni_number=client_data.dni_number,
                        phone=client_data.phone,
                    )
                )
            except Exception as e:
                # Log error but don't fail the client creation
                logger.error(
                    "Error sending client registration notification: %s",
                    str(e),
                    exc_info=True,
                )

            logger.info("Client created successfully: %s", client_model.id)
            return model_to_client_schema(client_model)

        except Exception as e:
            logger.error("Error creating client: %s", str(e), exc_info=True)
            raise InternalServerError(
                detail=f"Failed to create client: {str(e)}"
            ) from e

    @staticmethod
    def get_client_by_id(
        db: Session, client_id: UUID, include_biometrics: bool = False
    ) -> Optional[Client]:
        """
        Retrieve a client by their ID.

        Args:
            db: Database session
            client_id: Client UUID
            include_biometrics: Whether to include biometric summary in response

        Returns:
            Client schema instance if found, None otherwise
        """
        try:
            if include_biometrics:
                client_model = ClientRepository.get_by_id_with_biometrics(db, client_id)
            else:
                client_model = ClientRepository.get_by_id(db, client_id)

            if client_model:
                return model_to_client_schema(client_model)
            return None

        except Exception as e:
            logger.error(
                "Error retrieving client by ID %s: %s", client_id, str(e), exc_info=True
            )
            raise InternalServerError(
                detail=f"Failed to retrieve client: {str(e)}"
            ) from e

    @staticmethod
    def update_client(
        db: Session, client_id: UUID, client_update: ClientUpdate
    ) -> Optional[Client]:
        """
        Update an existing client's information.

        Args:
            db: Database session
            client_id: Client UUID to update
            client_update: Client update data

        Returns:
            Updated Client schema instance if found, None otherwise

        Raises:
            InternalServerError: If update fails
        """
        try:
            update_dict = {}

            if client_update.dni_type is not None:
                update_dict["dni_type"] = document_type_schema_to_enum(
                    client_update.dni_type
                )
            if client_update.dni_number is not None:
                update_dict["dni_number"] = client_update.dni_number
            if client_update.first_name is not None:
                update_dict["first_name"] = client_update.first_name
            if client_update.middle_name is not None:
                update_dict["middle_name"] = client_update.middle_name
            if client_update.last_name is not None:
                update_dict["last_name"] = client_update.last_name
            if client_update.second_last_name is not None:
                update_dict["second_last_name"] = client_update.second_last_name
            if client_update.phone is not None:
                update_dict["phone"] = client_update.phone
            if client_update.alternative_phone is not None:
                update_dict["alternative_phone"] = client_update.alternative_phone
            if client_update.birth_date is not None:
                update_dict["birth_date"] = client_update.birth_date
            if client_update.gender is not None:
                update_dict["gender"] = gender_type_schema_to_enum(client_update.gender)
            if client_update.address is not None:
                update_dict["address"] = client_update.address
            if client_update.is_active is not None:
                update_dict["is_active"] = client_update.is_active

            if not update_dict:
                # No updates provided, return current client
                return ClientService.get_client_by_id(db, client_id)

            client_model = ClientRepository.update(db, client_id, **update_dict)

            if client_model:
                logger.info("Client updated successfully: %s", client_id)
                return model_to_client_schema(client_model)

            return None

        except Exception as e:
            logger.error(
                "Error updating client %s: %s", client_id, str(e), exc_info=True
            )
            raise InternalServerError(
                detail=f"Failed to update client: {str(e)}"
            ) from e

    @staticmethod
    def delete_client(db: Session, client_id: UUID) -> bool:
        """
        Soft delete a client by setting is_active to False.

        Args:
            db: Database session
            client_id: Client UUID to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            result = ClientRepository.delete(db, client_id)
            if result:
                logger.info("Client deleted successfully: %s", client_id)
            return result

        except Exception as e:
            logger.error(
                "Error deleting client %s: %s", client_id, str(e), exc_info=True
            )
            raise InternalServerError(
                detail=f"Failed to delete client: {str(e)}"
            ) from e

    @staticmethod
    def list_clients(
        db: Session,
        is_active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Client]:
        """
        Retrieve a list of clients with optional filtering and pagination.

        Args:
            db: Database session
            is_active: Optional filter by active status
            limit: Maximum number of clients to return
            offset: Number of clients to skip for pagination

        Returns:
            List of Client schema instances
        """
        try:
            client_models = ClientRepository.get_all(db, is_active, limit, offset)
            return models_to_client_schemas(client_models)

        except Exception as e:
            logger.error("Error listing clients: %s", str(e), exc_info=True)
            raise InternalServerError(
                detail=f"Failed to list clients: {str(e)}"
            ) from e

    @staticmethod
    def search_clients(db: Session, search_term: str, limit: int = 50) -> List[Client]:
        """
        Search clients by name, DNI, or phone number.

        Args:
            db: Database session
            search_term: Search keyword
            limit: Maximum number of results to return

        Returns:
            List of matching Client schema instances
        """
        try:
            client_models = ClientRepository.search(db, search_term, limit)
            return models_to_client_schemas(client_models)

        except Exception as e:
            logger.error(
                "Error searching clients with term '%s': %s",
                search_term,
                str(e),
                exc_info=True,
            )
            raise InternalServerError(
                detail=f"Failed to search clients: {str(e)}"
            ) from e

    @staticmethod
    def get_client_by_dni(db: Session, dni_number: str) -> Optional[Client]:
        """
        Retrieve a client by their DNI (identification number).

        Args:
            db: Database session
            dni_number: DNI number to search for

        Returns:
            Client schema instance if found, None otherwise
        """
        try:
            client_model = ClientRepository.get_by_dni(db, dni_number)
            if client_model:
                return model_to_client_schema(client_model)
            return None

        except Exception as e:
            logger.error(
                "Error retrieving client by DNI '%s': %s",
                dni_number,
                str(e),
                exc_info=True,
            )
            raise InternalServerError(
                detail=f"Failed to retrieve client by DNI: {str(e)}"
            ) from e

    @staticmethod
    def get_client_dashboard(db: Session, client_id: UUID) -> Optional[ClientDashboard]:
        """
        Get comprehensive client dashboard data.

        Aggregates client information, biometric data, subscription status,
        and attendance statistics in a single operation.

        Args:
            db: Database session
            client_id: Client UUID

        Returns:
            ClientDashboard schema instance if found, None otherwise

        Raises:
            InternalServerError: If dashboard data retrieval fails
        """
        try:
            dashboard_data = ClientRepository.get_client_dashboard_data(db, client_id)

            if not dashboard_data:
                return None

            client_model = dashboard_data["client"]
            latest_subscription = dashboard_data["latest_subscription"]
            total_subscriptions = dashboard_data["total_subscriptions"]
            last_attendance = dashboard_data["last_attendance"]
            attendance_count = dashboard_data["attendance_count"]

            # Convert client model to basic info
            client = ClientBasicInfo(
                id=client_model.id,
                first_name=client_model.first_name,
                last_name=client_model.last_name,
                dni_type=client_model.dni_type.value,
                dni_number=client_model.dni_number,
                phone=client_model.phone,
                is_active=client_model.is_active,
                created_at=client_model.created_at,
                updated_at=client_model.updated_at,
            )

            # Extract biometric information
            biometric_type = None
            thumbnail_data_uri = None
            biometric_updated_at = None

            if hasattr(client_model, "biometrics") and client_model.biometrics:
                face_biometrics = [
                    bio
                    for bio in client_model.biometrics
                    if bio.type == BiometricTypeEnum.FACE
                ]

                if face_biometrics:
                    active_face = next(
                        (bio for bio in face_biometrics if bio.is_active), None
                    )
                    target_biometric = active_face if active_face else face_biometrics[0]

                    biometric_type = target_biometric.type.value
                    biometric_updated_at = target_biometric.updated_at.isoformat()

                    if target_biometric.thumbnail:
                        try:
                            encryption_service = get_encryption_service()
                            decrypted_thumbnail = encryption_service.decrypt_image_data(
                                target_biometric.thumbnail
                            )
                            thumbnail_base64 = base64.b64encode(
                                decrypted_thumbnail
                            ).decode("utf-8")
                            thumbnail_data_uri = (
                                f"data:image/jpeg;base64,{thumbnail_base64}"
                            )
                        except Exception as e:
                            logger.warning(
                                "Error decrypting thumbnail for client %s: %s",
                                client_id,
                                str(e),
                            )

            biometric = BiometricInfo(
                type=biometric_type,
                thumbnail=thumbnail_data_uri,
                updated_at=biometric_updated_at
                or client_model.updated_at.isoformat(),
            )

            # Extract subscription information
            subscription_status = None
            subscription_plan = None
            subscription_end_date = None

            if latest_subscription:
                subscription_status = (
                    latest_subscription.status.value.replace("_", " ").title()
                )
                if hasattr(latest_subscription, "plan") and latest_subscription.plan:
                    subscription_plan = latest_subscription.plan.name
                subscription_end_date = latest_subscription.end_date.isoformat()

            subscription = SubscriptionInfo(
                status=subscription_status,
                plan=subscription_plan,
                end_date=subscription_end_date,
            )

            # Create statistics
            stats = ClientStats(
                subscriptions=total_subscriptions,
                attendances=attendance_count,
                last_attendance=(
                    last_attendance.check_in.isoformat() if last_attendance else None
                ),
                since=client_model.created_at.isoformat(),
            )

            return ClientDashboard(
                client=client,
                biometric=biometric,
                subscription=subscription,
                stats=stats,
            )

        except Exception as e:
            logger.error(
                "Error retrieving client dashboard for %s: %s",
                client_id,
                str(e),
                exc_info=True,
            )
            raise InternalServerError(
                detail=f"Failed to retrieve client dashboard: {str(e)}"
            ) from e
