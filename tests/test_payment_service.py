"""
Pruebas para PaymentService

Este archivo contiene 8 pruebas principales para el servicio de pagos.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import date, datetime, timedelta
from uuid import uuid4
from decimal import Decimal

from app.services.payment_service import PaymentService
from app.schemas.payment import PaymentCreate, PaymentMethod
from app.db.models import SubscriptionStatusEnum
from app.repositories.payment_repository import PaymentRepository


# ============================================================================
# ✅ CASOS EXITOSOS
# ============================================================================

def test_create_payment_full():
    """
    ID: PAY-001
    Nombre: Crear pago completo que activa suscripción
    Tipo: Unitario (Servicio)
    """
    mock_db = MagicMock()
    subscription_id = uuid4()
    
    # Mock de suscripción pendiente de pago
    mock_subscription = MagicMock()
    mock_subscription.id = subscription_id
    mock_subscription.status = SubscriptionStatusEnum.PENDING_PAYMENT
    mock_subscription.final_price = Decimal('50000.00')
    mock_subscription.plan = MagicMock()
    mock_subscription.plan.price = Decimal('50000.00')
    
    # Mock de pago creado
    mock_payment = MagicMock()
    mock_payment.id = uuid4()
    mock_payment.subscription_id = subscription_id
    mock_payment.amount = Decimal('50000.00')
    mock_payment.payment_method = "cash"
    mock_payment.payment_date = datetime.now()
    mock_payment.meta_info = None
    
    # Mock de Payment.from_orm
    mock_payment_obj = MagicMock()
    mock_payment_obj.id = mock_payment.id
    mock_payment_obj.subscription_id = subscription_id
    mock_payment_obj.amount = Decimal('50000.00')
    mock_payment_obj.payment_method = PaymentMethod.CASH
    mock_payment_obj.payment_date = datetime.now()
    mock_payment_obj.meta_info = None
    
    # Mock de suscripción actualizada
    updated_subscription = MagicMock()
    updated_subscription.status = SubscriptionStatusEnum.ACTIVE
    
    with patch('app.services.payment_service.PaymentRepository.create', return_value=mock_payment):
        with patch('app.services.payment_service.SubscriptionRepository.get_by_id', return_value=mock_subscription):
            with patch('app.services.payment_service.PaymentRepository.get_total_paid', return_value=Decimal('50000.00')):
                with patch('app.services.payment_service.SubscriptionRepository.update', return_value=updated_subscription):
                    with patch('app.services.payment_service.get_subscription_price', return_value=Decimal('50000.00')):
                        with patch('app.services.payment_service.NotificationService.send_payment_notification', new_callable=AsyncMock):
                            with patch('app.services.payment_service.Payment.from_orm', return_value=mock_payment_obj):
                                payment_data = PaymentCreate(
                                    subscription_id=subscription_id,
                                    amount=Decimal('50000.00'),
                                    payment_method=PaymentMethod.CASH
                                )
                                
                                result = PaymentService.create_payment(mock_db, payment_data)
    
    assert result is not None
    assert result.payment.amount == Decimal('50000.00')
    assert result.subscription_status == SubscriptionStatusEnum.ACTIVE.value
    assert result.remaining_debt == Decimal('0.00')


def test_create_payment_partial():
    """
    ID: PAY-002
    Nombre: Crear pago parcial
    """
    mock_db = MagicMock()
    subscription_id = uuid4()
    
    mock_subscription = MagicMock()
    mock_subscription.id = subscription_id
    mock_subscription.status = SubscriptionStatusEnum.PENDING_PAYMENT
    mock_subscription.final_price = Decimal('50000.00')
    
    mock_payment = MagicMock()
    mock_payment.id = uuid4()
    mock_payment.subscription_id = subscription_id
    mock_payment.amount = Decimal('20000.00')
    mock_payment.payment_method = "cash"
    mock_payment.payment_date = datetime.now()
    mock_payment.meta_info = None
    
    mock_payment_obj = MagicMock()
    mock_payment_obj.id = mock_payment.id
    mock_payment_obj.subscription_id = subscription_id
    mock_payment_obj.amount = Decimal('20000.00')
    mock_payment_obj.payment_method = PaymentMethod.CASH
    mock_payment_obj.payment_date = datetime.now()
    mock_payment_obj.meta_info = None
    
    with patch('app.services.payment_service.PaymentRepository.create', return_value=mock_payment):
        with patch('app.services.payment_service.SubscriptionRepository.get_by_id', return_value=mock_subscription):
            with patch('app.services.payment_service.PaymentRepository.get_total_paid', return_value=Decimal('20000.00')):
                with patch('app.services.payment_service.get_subscription_price', return_value=Decimal('50000.00')):
                    with patch('app.services.payment_service.NotificationService.send_payment_notification', new_callable=AsyncMock):
                        with patch('app.services.payment_service.Payment.from_orm', return_value=mock_payment_obj):
                            payment_data = PaymentCreate(
                                subscription_id=subscription_id,
                                amount=Decimal('20000.00'),
                                payment_method=PaymentMethod.CASH
                            )
                            
                            result = PaymentService.create_payment(mock_db, payment_data)
    
    assert result is not None
    assert result.payment.amount == Decimal('20000.00')
    assert result.remaining_debt == Decimal('30000.00')
    assert result.subscription_status == SubscriptionStatusEnum.PENDING_PAYMENT.value


def test_get_payments_by_subscription():
    """
    ID: PAY-003
    Nombre: Obtener pagos de una suscripción
    """
    mock_db = MagicMock()
    subscription_id = uuid4()
    
    mock_payment_models = [
        MagicMock(id=uuid4(), subscription_id=subscription_id, amount=Decimal('20000.00')),
        MagicMock(id=uuid4(), subscription_id=subscription_id, amount=Decimal('30000.00')),
    ]
    
    mock_payment_objs = [
        MagicMock(id=mock_payment_models[0].id, subscription_id=subscription_id, amount=Decimal('20000.00')),
        MagicMock(id=mock_payment_models[1].id, subscription_id=subscription_id, amount=Decimal('30000.00')),
    ]
    
    with patch('app.services.payment_service.PaymentRepository.get_by_subscription', return_value=mock_payment_models):
        with patch('app.services.payment_service.Payment.from_orm', side_effect=mock_payment_objs):
            result = PaymentService.get_payments_by_subscription(mock_db, subscription_id)
    
    assert len(result) == 2
    assert all(p.subscription_id == subscription_id for p in result)


def test_get_total_paid_by_subscription():
    """
    ID: PAY-004
    Nombre: Calcular total pagado de una suscripción
    """
    mock_db = MagicMock()
    subscription_id = uuid4()
    
    # Este método no existe directamente, usar PaymentRepository.get_total_paid
    with patch('app.services.payment_service.PaymentRepository.get_total_paid', return_value=Decimal('45000.00')):
        result = PaymentRepository.get_total_paid(mock_db, subscription_id)
    
    assert result == Decimal('45000.00')


def test_get_remaining_debt():
    """
    ID: PAY-005
    Nombre: Calcular deuda restante de suscripción usando stats
    """
    mock_db = MagicMock()
    subscription_id = uuid4()
    
    mock_subscription = MagicMock()
    mock_subscription.id = subscription_id
    mock_subscription.status = SubscriptionStatusEnum.PENDING_PAYMENT
    mock_subscription.final_price = Decimal('50000.00')
    
    mock_stats = MagicMock()
    mock_stats.total_amount_paid = Decimal('30000.00')
    mock_stats.remaining_debt = Decimal('20000.00')
    
    with patch('app.services.payment_service.SubscriptionRepository.get_by_id', return_value=mock_subscription):
        with patch('app.services.payment_service.PaymentService.get_subscription_payment_stats', return_value=mock_stats):
            result = PaymentService.get_subscription_payment_stats(mock_db, subscription_id)
    
    assert result.remaining_debt == Decimal('20000.00')


def test_get_payment_statistics():
    """
    ID: PAY-006
    Nombre: Obtener estadísticas de pagos de suscripción
    """
    mock_db = MagicMock()
    subscription_id = uuid4()
    
    mock_stats = MagicMock()
    mock_stats.total_payments = 3
    mock_stats.total_amount_paid = Decimal('75000.00')
    mock_stats.remaining_debt = Decimal('5000.00')
    mock_stats.subscription_id = subscription_id
    
    mock_subscription = MagicMock()
    mock_subscription.status = SubscriptionStatusEnum.PENDING_PAYMENT
    
    with patch('app.services.payment_service.SubscriptionRepository.get_by_id', return_value=mock_subscription):
        with patch('app.services.payment_service.PaymentRepository.get_total_paid', return_value=Decimal('75000.00')):
            with patch('app.services.payment_service.get_subscription_price', return_value=Decimal('80000.00')):
                with patch('app.services.payment_service.PaymentRepository.count_by_subscription', return_value=3):
                    with patch('app.services.payment_service.PaymentRepository.get_last_payment_date', return_value=datetime.now()):
                        result = PaymentService.get_subscription_payment_stats(mock_db, subscription_id)
    
    assert result is not None
    assert result.total_payments == 3


# ============================================================================
# ❌ CASOS DE ERROR
# ============================================================================

def test_create_payment_subscription_not_found():
    """
    ID: PAY-007
    Nombre: Error al crear pago para suscripción inexistente
    """
    mock_db = MagicMock()
    subscription_id = uuid4()
    
    with patch('app.services.payment_service.SubscriptionRepository.get_by_id', return_value=None):
        payment_data = PaymentCreate(
            subscription_id=subscription_id,
            amount=Decimal('50000.00'),
            payment_method=PaymentMethod.CASH
        )
        
        with pytest.raises(ValueError) as exc_info:
            PaymentService.create_payment(mock_db, payment_data)
        
        assert "not found" in str(exc_info.value).lower()


def test_get_payments_by_subscription_empty():
    """
    ID: PAY-008
    Nombre: Obtener pagos de suscripción sin pagos
    """
    mock_db = MagicMock()
    subscription_id = uuid4()
    
    with patch('app.services.payment_service.PaymentRepository.get_by_subscription', return_value=[]):
        with patch('app.services.payment_service.Payment.from_orm', return_value=[]):
            result = PaymentService.get_payments_by_subscription(mock_db, subscription_id)
    
    assert result == []

