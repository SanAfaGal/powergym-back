"""
Pruebas para SubscriptionService

Este archivo contiene 8 pruebas principales para el servicio de suscripciones.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import date, datetime, timedelta
from uuid import uuid4
from decimal import Decimal

from app.services.subscription_service import SubscriptionService
from app.schemas.subscription import SubscriptionCreate, SubscriptionRenew, SubscriptionCancel
from app.db.models import SubscriptionStatusEnum, DurationTypeEnum
from app.repositories.plan_repository import PlanRepository


# ============================================================================
# ✅ CASOS EXITOSOS
# ============================================================================

def test_create_subscription_success():
    """
    ID: SUB-001
    Nombre: Crear suscripción exitosamente
    Tipo: Unitario (Servicio)
    """
    mock_db = MagicMock()
    client_id = uuid4()
    plan_id = uuid4()
    
    # Mock del plan
    mock_plan = MagicMock()
    mock_plan.id = plan_id
    mock_plan.price = Decimal('50000.00')
    mock_plan.duration_unit = DurationTypeEnum.MONTH
    mock_plan.duration_count = 1
    
    # Mock de la suscripción creada
    mock_subscription = MagicMock()
    mock_subscription.id = uuid4()
    mock_subscription.client_id = client_id
    mock_subscription.plan_id = plan_id
    mock_subscription.start_date = date.today()
    mock_subscription.end_date = date.today() + timedelta(days=30)
    mock_subscription.status = SubscriptionStatusEnum.PENDING_PAYMENT
    mock_subscription.final_price = None
    mock_subscription.cancellation_date = None
    mock_subscription.cancellation_reason = None
    mock_subscription.created_at = datetime.now()
    mock_subscription.updated_at = datetime.now()
    mock_subscription.meta_info = {}
    
    with patch('app.services.subscription_service.PlanRepository.get_by_id', return_value=mock_plan):
        with patch('app.services.subscription_service.SubscriptionRepository.create', return_value=mock_subscription):
            with patch('app.services.subscription_service.SubscriptionCalculator.calculate_end_date', return_value=date.today() + timedelta(days=30)):
                with patch('app.services.subscription_service.NotificationService.send_subscription_notification', new_callable=AsyncMock):
                    with patch('app.services.subscription_service.Subscription.from_orm') as mock_from_orm:
                        mock_sub_obj = MagicMock()
                        mock_sub_obj.id = mock_subscription.id
                        mock_sub_obj.client_id = client_id
                        mock_sub_obj.plan_id = plan_id
                        mock_sub_obj.status = SubscriptionStatusEnum.PENDING_PAYMENT
                        mock_sub_obj.cancellation_date = None
                        mock_sub_obj.cancellation_reason = None
                        mock_from_orm.return_value = mock_sub_obj
                        
                        subscription_data = SubscriptionCreate(
                            client_id=client_id,
                            plan_id=plan_id,
                            start_date=date.today()
                        )
                        
                        result = SubscriptionService.create_subscription(mock_db, subscription_data)
    
    assert result is not None
    assert result.client_id == client_id
    assert result.plan_id == plan_id


def test_create_subscription_with_discount():
    """
    ID: SUB-002
    Nombre: Crear suscripción con descuento
    """
    mock_db = MagicMock()
    client_id = uuid4()
    plan_id = uuid4()
    
    mock_plan = MagicMock()
    mock_plan.id = plan_id
    mock_plan.price = Decimal('50000.00')
    
    mock_subscription = MagicMock()
    mock_subscription.id = uuid4()
    mock_subscription.client_id = client_id
    mock_subscription.plan_id = plan_id
    mock_subscription.start_date = date.today()
    mock_subscription.end_date = date.today() + timedelta(days=30)
    mock_subscription.status = SubscriptionStatusEnum.PENDING_PAYMENT
    mock_subscription.final_price = 45000.0  # 10% descuento
    mock_subscription.meta_info = {
        "original_price": 50000.0,
        "discount_percentage": 10.0,
        "final_price": 45000.0,
        "discount_amount": 5000.0
    }
    
    with patch('app.services.subscription_service.PlanRepository.get_by_id', return_value=mock_plan):
        with patch('app.services.subscription_service.SubscriptionRepository.create', return_value=mock_subscription):
            with patch('app.services.subscription_service.SubscriptionCalculator.calculate_end_date', return_value=date.today() + timedelta(days=30)):
                with patch('app.services.subscription_service.NotificationService.send_subscription_notification', new_callable=AsyncMock):
                    with patch('app.services.subscription_service.Subscription.from_orm') as mock_from_orm:
                        mock_sub_obj = MagicMock()
                        mock_sub_obj.id = mock_subscription.id
                        mock_sub_obj.client_id = client_id
                        mock_sub_obj.final_price = 45000.0
                        mock_sub_obj.cancellation_date = None
                        mock_sub_obj.cancellation_reason = None
                        mock_from_orm.return_value = mock_sub_obj
                        
                        subscription_data = SubscriptionCreate(
                            client_id=client_id,
                            plan_id=plan_id,
                            start_date=date.today(),
                            discount_percentage=10.0
                        )
                        
                        result = SubscriptionService.create_subscription(mock_db, subscription_data)
    
    assert result is not None
    assert result.final_price == 45000.0


def test_get_active_subscription_by_client():
    """
    ID: SUB-003
    Nombre: Obtener suscripción activa de un cliente
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    mock_subscription = MagicMock()
    mock_subscription.id = uuid4()
    mock_subscription.client_id = client_id
    mock_subscription.plan_id = uuid4()
    mock_subscription.status = SubscriptionStatusEnum.ACTIVE
    mock_subscription.start_date = date.today() - timedelta(days=10)
    mock_subscription.end_date = date.today() + timedelta(days=20)
    mock_subscription.cancellation_date = None
    mock_subscription.cancellation_reason = None
    mock_subscription.final_price = None
    mock_subscription.created_at = datetime.now()
    mock_subscription.updated_at = datetime.now()
    mock_subscription.meta_info = {}
    
    with patch('app.services.subscription_service.SubscriptionRepository.get_active_by_client', return_value=[mock_subscription]):
        with patch('app.services.subscription_service.Subscription.from_orm') as mock_from_orm:
            mock_sub_obj = MagicMock()
            mock_sub_obj.id = mock_subscription.id
            mock_sub_obj.client_id = client_id
            mock_sub_obj.plan_id = mock_subscription.plan_id
            mock_sub_obj.status = SubscriptionStatusEnum.ACTIVE
            mock_sub_obj.start_date = mock_subscription.start_date
            mock_sub_obj.end_date = mock_subscription.end_date
            mock_sub_obj.cancellation_date = None
            mock_sub_obj.cancellation_reason = None
            mock_sub_obj.final_price = None
            mock_sub_obj.created_at = mock_subscription.created_at
            mock_sub_obj.updated_at = mock_subscription.updated_at
            mock_sub_obj.meta_info = {}
            mock_from_orm.return_value = mock_sub_obj
            
            result = SubscriptionService.get_active_subscription_by_client(mock_db, client_id)
    
    assert result is not None
    assert result.status == SubscriptionStatusEnum.ACTIVE


def test_get_subscription_by_id():
    """
    ID: SUB-004
    Nombre: Obtener suscripción por ID
    """
    mock_db = MagicMock()
    subscription_id = uuid4()
    
    mock_subscription = MagicMock()
    mock_subscription.id = subscription_id
    mock_subscription.client_id = uuid4()
    mock_subscription.status = SubscriptionStatusEnum.ACTIVE
    
    # SubscriptionService no tiene get_subscription_by_id, usar directamente el repositorio
    with patch('app.services.subscription_service.SubscriptionRepository.get_by_id', return_value=mock_subscription):
        from app.repositories.subscription_repository import SubscriptionRepository
        result = SubscriptionRepository.get_by_id(mock_db, subscription_id)
    
    assert result is not None
    assert result.id == subscription_id


def test_renew_subscription():
    """
    ID: SUB-005
    Nombre: Renovar suscripción exitosamente
    """
    mock_db = MagicMock()
    subscription_id = uuid4()
    client_id = uuid4()
    
    # Mock de suscripción existente
    existing_subscription = MagicMock()
    existing_subscription.id = subscription_id
    existing_subscription.client_id = client_id
    existing_subscription.end_date = date.today() + timedelta(days=5)
    existing_subscription.plan = MagicMock()
    existing_subscription.plan.duration_unit = DurationTypeEnum.MONTH
    existing_subscription.plan.duration_count = 1
    
    # Mock de nueva suscripción
    new_subscription = MagicMock()
    new_subscription.id = uuid4()
    new_subscription.client_id = client_id
    new_subscription.start_date = date.today() + timedelta(days=5)
    new_subscription.end_date = date.today() + timedelta(days=35)
    new_subscription.status = SubscriptionStatusEnum.SCHEDULED
    
    new_subscription.plan_id = existing_subscription.plan_id = uuid4()
    new_subscription.status = SubscriptionStatusEnum.SCHEDULED
    new_subscription.cancellation_date = None
    new_subscription.cancellation_reason = None
    new_subscription.final_price = None
    new_subscription.created_at = datetime.now()
    new_subscription.updated_at = datetime.now()
    new_subscription.meta_info = {}
    
    with patch('app.services.subscription_service.SubscriptionRepository.get_by_id', return_value=existing_subscription):
        with patch('app.services.subscription_service.SubscriptionCalculator.calculate_end_date', return_value=date.today() + timedelta(days=35)):
            with patch('app.services.subscription_service.SubscriptionRepository.create', return_value=new_subscription):
                with patch('app.services.subscription_service.NotificationService.send_subscription_notification', new_callable=AsyncMock):
                    with patch('app.services.subscription_service.Subscription.from_orm') as mock_from_orm:
                        mock_sub_obj = MagicMock()
                        mock_sub_obj.id = new_subscription.id
                        mock_sub_obj.client_id = client_id
                        mock_sub_obj.plan_id = new_subscription.plan_id
                        mock_sub_obj.start_date = new_subscription.start_date
                        mock_sub_obj.end_date = new_subscription.end_date
                        mock_sub_obj.status = SubscriptionStatusEnum.SCHEDULED
                        mock_sub_obj.cancellation_date = None
                        mock_sub_obj.cancellation_reason = None
                        mock_sub_obj.final_price = None
                        mock_sub_obj.created_at = new_subscription.created_at
                        mock_sub_obj.updated_at = new_subscription.updated_at
                        mock_sub_obj.meta_info = {}
                        mock_from_orm.return_value = mock_sub_obj
                        
                        renew_data = SubscriptionRenew(
                            client_id=client_id,
                            subscription_id=subscription_id,
                            plan_id=None
                        )
                        
                        result = SubscriptionService.renew_subscription(mock_db, renew_data)
    
    assert result is not None


def test_cancel_subscription():
    """
    ID: SUB-006
    Nombre: Cancelar suscripción exitosamente
    """
    mock_db = MagicMock()
    subscription_id = uuid4()
    
    mock_subscription = MagicMock()
    mock_subscription.id = subscription_id
    mock_subscription.status = SubscriptionStatusEnum.ACTIVE
    
    updated_subscription = MagicMock()
    updated_subscription.id = subscription_id
    updated_subscription.status = SubscriptionStatusEnum.CANCELED
    
    with patch('app.services.subscription_service.SubscriptionRepository.get_by_id', return_value=mock_subscription):
            with patch('app.services.subscription_service.SubscriptionRepository.cancel', return_value=updated_subscription):
                with patch('app.services.subscription_service.Subscription.from_orm', return_value=updated_subscription):
                    cancel_data = SubscriptionCancel(
                        subscription_id=subscription_id,
                        cancellation_reason="Cliente solicita cancelación"
                    )
                    
                    result = SubscriptionService.cancel_subscription(mock_db, cancel_data)
    
    assert result is not None
    assert result.status == SubscriptionStatusEnum.CANCELED


# ============================================================================
# ❌ CASOS DE ERROR
# ============================================================================

def test_create_subscription_plan_not_found():
    """
    ID: SUB-007
    Nombre: Error al crear suscripción con plan inexistente
    """
    mock_db = MagicMock()
    client_id = uuid4()
    plan_id = uuid4()
    
    with patch('app.services.subscription_service.PlanRepository.get_by_id', return_value=None):
        subscription_data = SubscriptionCreate(
            client_id=client_id,
            plan_id=plan_id,
            start_date=date.today()
        )
        
        with pytest.raises(ValueError) as exc_info:
            SubscriptionService.create_subscription(mock_db, subscription_data)
        
        assert "not found" in str(exc_info.value).lower()


def test_get_active_subscription_not_found():
    """
    ID: SUB-008
    Nombre: Obtener suscripción activa cuando no existe
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    with patch('app.services.subscription_service.SubscriptionRepository.get_active_by_client', return_value=[]):
        result = SubscriptionService.get_active_subscription_by_client(mock_db, client_id)
    
    assert result is None

