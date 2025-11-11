"""
Pruebas para SubscriptionRepository

Este archivo contiene 8 pruebas principales para el repositorio de suscripciones.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import date, timedelta
from uuid import uuid4
from decimal import Decimal

from app.repositories.subscription_repository import SubscriptionRepository
from app.db.models import SubscriptionStatusEnum, DurationTypeEnum


# ============================================================================
# ✅ CASOS EXITOSOS
# ============================================================================

def test_create_subscription():
    """
    ID: REPSUB-001
    Nombre: Crear suscripción en base de datos
    Tipo: Unitario (Repositorio)
    """
    mock_db = MagicMock()
    client_id = uuid4()
    plan_id = uuid4()
    
    mock_subscription = MagicMock()
    mock_subscription.id = uuid4()
    mock_subscription.client_id = client_id
    mock_subscription.plan_id = plan_id
    mock_subscription.start_date = date.today()
    mock_subscription.end_date = date.today() + timedelta(days=30)
    mock_subscription.status = SubscriptionStatusEnum.PENDING_PAYMENT
    
    with patch('app.repositories.subscription_repository.SubscriptionModel', return_value=mock_subscription):
        result = SubscriptionRepository.create(
            db=mock_db,
            client_id=client_id,
            plan_id=plan_id,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status=SubscriptionStatusEnum.PENDING_PAYMENT
        )
    
    assert result == mock_subscription
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_get_by_id():
    """
    ID: REPSUB-002
    Nombre: Obtener suscripción existente por ID
    """
    mock_db = MagicMock()
    subscription_id = uuid4()
    
    expected = MagicMock()
    expected.id = subscription_id
    expected.client_id = uuid4()
    expected.status = SubscriptionStatusEnum.ACTIVE
    
    mock_db.query.return_value.filter.return_value.first.return_value = expected
    
    result = SubscriptionRepository.get_by_id(mock_db, subscription_id)
    
    assert result is not None
    assert result.id == subscription_id


def test_get_by_client_id():
    """
    ID: REPSUB-003
    Nombre: Obtener suscripciones de un cliente
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    expected_subscriptions = [
        MagicMock(id=uuid4(), client_id=client_id, status=SubscriptionStatusEnum.ACTIVE),
        MagicMock(id=uuid4(), client_id=client_id, status=SubscriptionStatusEnum.EXPIRED),
    ]
    
    mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.offset.return_value.all.return_value = expected_subscriptions
    
    result = SubscriptionRepository.get_by_client(mock_db, client_id)
    
    assert len(result) == 2
    assert all(sub.client_id == client_id for sub in result)


def test_get_active_by_client_id():
    """
    ID: REPSUB-004
    Nombre: Obtener suscripción activa de un cliente
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    mock_subscription = MagicMock()
    mock_subscription.id = uuid4()
    mock_subscription.client_id = client_id
    mock_subscription.status = SubscriptionStatusEnum.ACTIVE
    mock_subscription.end_date = date.today() + timedelta(days=20)
    
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_subscription]
    
    result = SubscriptionRepository.get_active_by_client(mock_db, client_id)
    
    assert len(result) == 1
    assert result[0].status == SubscriptionStatusEnum.ACTIVE
    assert result[0].client_id == client_id


def test_get_by_status():
    """
    ID: REPSUB-005
    Nombre: Obtener suscripciones por estado
    """
    mock_db = MagicMock()
    
    expected_subscriptions = [
        MagicMock(id=uuid4(), status=SubscriptionStatusEnum.ACTIVE),
        MagicMock(id=uuid4(), status=SubscriptionStatusEnum.ACTIVE),
    ]
    
    mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.offset.return_value.all.return_value = expected_subscriptions
    
    result = SubscriptionRepository.get_by_status(mock_db, SubscriptionStatusEnum.ACTIVE)
    
    assert len(result) == 2
    assert all(sub.status == SubscriptionStatusEnum.ACTIVE for sub in result)


def test_update_subscription():
    """
    ID: REPSUB-006
    Nombre: Actualizar suscripción existente
    """
    mock_db = MagicMock()
    subscription_id = uuid4()
    
    existing_subscription = MagicMock()
    existing_subscription.id = subscription_id
    existing_subscription.status = SubscriptionStatusEnum.PENDING_PAYMENT
    
    mock_db.query.return_value.filter.return_value.first.return_value = existing_subscription
    
    result = SubscriptionRepository.update(
        db=mock_db,
        subscription_id=subscription_id,
        status=SubscriptionStatusEnum.ACTIVE
    )
    
    assert result is not None
    mock_db.commit.assert_called_once()
    # refresh se llama con el objeto que se obtuvo del query
    mock_db.refresh.assert_called()


def test_get_expired_subscriptions():
    """
    ID: REPSUB-007
    Nombre: Obtener suscripciones expiradas
    """
    mock_db = MagicMock()
    
    expired_subscriptions = [
        MagicMock(id=uuid4(), end_date=date.today() - timedelta(days=1), status=SubscriptionStatusEnum.EXPIRED),
        MagicMock(id=uuid4(), end_date=date.today() - timedelta(days=5), status=SubscriptionStatusEnum.EXPIRED),
    ]
    
    mock_db.query.return_value.filter.return_value.all.return_value = expired_subscriptions
    
    result = SubscriptionRepository.get_expired(mock_db)
    
    assert len(result) == 2


# ============================================================================
# ❌ CASOS DE ERROR
# ============================================================================

def test_get_by_id_not_found():
    """
    ID: REPSUB-008
    Nombre: Obtener suscripción inexistente
    """
    mock_db = MagicMock()
    subscription_id = uuid4()
    
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    result = SubscriptionRepository.get_by_id(mock_db, subscription_id)
    
    assert result is None

