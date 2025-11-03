# ============================================================================
# attendance/service.py - SYNC VERSION
# ============================================================================

from datetime import datetime
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.attendance_repository import AttendanceRepository
from app.schemas.attendance import (
    AttendanceResponse,
    AttendanceWithClientInfo,
    AccessDenialReason
)
from app.db.models import ClientModel, SubscriptionModel
from app.utils.attendance import AccessValidationUtil
from app.utils.common.formatters import format_client_name
from app.services.notification_service import NotificationService
from app.core.async_processing import run_async_in_background
import logging

logger = logging.getLogger(__name__)


class AttendanceService:
    """
    Servicio de asistencias.

    Encapsula la lógica de negocio para crear, validar y consultar asistencias.
    """

    @staticmethod
    def create_attendance(
            db: Session,
            client_id: UUID,
            meta_info: Optional[dict] = None
    ) -> AttendanceResponse:
        """
        Crear un registro de asistencia.

        Args:
            db: Sesión de BD
            client_id: ID del cliente
            meta_info: Información adicional

        Returns:
            AttendanceResponse con los datos creados
        """
        attendance = AttendanceRepository.create(
            db=db,
            client_id=client_id,
            meta_info=meta_info or {}
        )

        # Send Telegram notification in background
        try:
            client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
            if client:
                # Format client name using utility function
                client_name = format_client_name(
                    first_name=client.first_name,
                    last_name=client.last_name,
                    middle_name=client.middle_name,
                    second_last_name=client.second_last_name
                )

                # Send notification asynchronously (fire and forget)
                run_async_in_background(
                    NotificationService.send_check_in_notification(
                        client_name=client_name,
                        dni_number=client.dni_number,
                        check_in_time=attendance.check_in
                    )
                )
        except Exception as e:
            # Log error but don't fail the attendance creation
            logger.error("Error sending check-in notification: %s", str(e), exc_info=True)

        return AttendanceResponse(
            id=attendance.id,
            client_id=attendance.client_id,
            check_in=attendance.check_in,
            meta_info=attendance.meta_info
        )

    @staticmethod
    def get_by_id(
            db: Session,
            attendance_id: UUID
    ) -> Optional[AttendanceResponse]:
        """Obtener una asistencia por ID."""
        attendance = AttendanceRepository.get_by_id(db, attendance_id)

        if not attendance:
            return None

        return AttendanceResponse(
            id=attendance.id,
            client_id=attendance.client_id,
            check_in=attendance.check_in,
            meta_info=attendance.meta_info
        )

    @staticmethod
    def get_client_attendances(
            db: Session,
            client_id: UUID,
            limit: int = 50,
            offset: int = 0
    ) -> List[AttendanceResponse]:
        """Obtener historial de asistencias de un cliente."""
        attendances = AttendanceRepository.get_by_client_id(
            db, client_id, limit, offset
        )

        return [
            AttendanceResponse(
                id=att.id,
                client_id=att.client_id,
                check_in=att.check_in,
                meta_info=att.meta_info
            )
            for att in attendances
        ]

    @staticmethod
    def get_all_attendances(
            db: Session,
            limit: int = 100,
            offset: int = 0,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None
    ) -> List[AttendanceWithClientInfo]:
        """Obtener todas las asistencias con información del cliente."""
        rows = AttendanceRepository.get_with_client_info(
            db=db,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date
        )

        return [
            AttendanceWithClientInfo(
                id=att.id,
                client_id=att.client_id,
                check_in=att.check_in,
                meta_info=att.meta_info,
                client_first_name=first_name,
                client_last_name=last_name,
                client_dni_number=dni_number
            )
            for att, first_name, last_name, dni_number in rows
        ]

    @staticmethod
    def validate_client_access(
            db: Session,
            client_id: UUID
    ) -> Tuple[bool, Optional[str], Optional[dict]]:
        """
        Validar si un cliente puede acceder.

        Returns:
            (can_access, reason, details)
        """
        # 1. Cliente existe y activo
        client = db.query(ClientModel).filter(
            ClientModel.id == client_id
        ).first()

        if not client:
            return False, AccessDenialReason.CLIENT_NOT_FOUND, None

        if not client.is_active:
            return False, AccessDenialReason.CLIENT_INACTIVE, None

        # 2. Verificar si ya tiene asistencia hoy
        existing_attendance = AttendanceRepository.get_today_attendance(db, client_id)
        if existing_attendance:
            return (
                False,
                AccessDenialReason.ALREADY_CHECKED_IN,
                {
                    "check_in_time": existing_attendance.check_in.isoformat(),
                    "client_info": AccessValidationUtil.format_client_info(client)
                }
            )

        # 3. Suscripción activa
        subscription = AttendanceService._get_active_subscription(db, client_id)

        if not subscription:
            return False, AccessDenialReason.NO_SUBSCRIPTION, None

        # 4. Suscripción no expirada
        if subscription.end_date < datetime.now().date():
            return (
                False,
                AccessDenialReason.SUBSCRIPTION_EXPIRED,
                {
                    "expired_date": subscription.end_date.isoformat()
                }
            )

        return True, None, AccessValidationUtil.format_client_info(client)

    @staticmethod
    def _get_active_subscription(
            db: Session,
            client_id: UUID
    ) -> Optional[SubscriptionModel]:
        """Obtener suscripción activa de un cliente."""
        return db.query(SubscriptionModel).filter(
            SubscriptionModel.client_id == client_id,
            SubscriptionModel.status == "active"
        ).order_by(
            SubscriptionModel.end_date.desc()
        ).first()
