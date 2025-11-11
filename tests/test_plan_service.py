"""
Pruebas para PlanService

Este archivo contiene 8 pruebas principales para el servicio de planes.
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from decimal import Decimal

from app.services.plan_service import PlanService
from app.schemas.plan import PlanCreate, PlanUpdate
from app.db.models import DurationTypeEnum


# ============================================================================
# ✅ CASOS EXITOSOS
# ============================================================================

def test_create_plan_success():
    """
    ID: PLN-001
    Nombre: Crear plan exitosamente
    Tipo: Unitario (Servicio)
    """
    mock_db = MagicMock()
    
    mock_plan = MagicMock()
    mock_plan.id = uuid4()
    mock_plan.name = "Plan Mensual"
    mock_plan.slug = "plan-mensual"
    mock_plan.price = Decimal('50000.00')
    mock_plan.duration_unit = DurationTypeEnum.MONTH
    mock_plan.duration_count = 1
    mock_plan.is_active = True
    
    with patch('app.services.plan_service.PlanRepository.create', return_value=mock_plan):
        plan_data = PlanCreate(
            name="Plan Mensual",
            slug="plan-mensual",
            description="Plan mensual básico",
            price=Decimal('50000.00'),
            currency="COP",
            duration_unit="month",
            duration_count=1
        )
        
        result = PlanService.create_plan(mock_db, plan_data)
    
    assert result is not None
    assert result.name == "Plan Mensual"
    assert result.price == Decimal('50000.00')


def test_get_plan_by_id_success():
    """
    ID: PLN-002
    Nombre: Obtener plan por ID existente
    """
    mock_db = MagicMock()
    plan_id = uuid4()
    
    mock_plan = MagicMock()
    mock_plan.id = plan_id
    mock_plan.name = "Plan Mensual"
    mock_plan.is_active = True
    
    with patch('app.services.plan_service.PlanRepository.get_by_id', return_value=mock_plan):
        result = PlanService.get_plan_by_id(mock_db, plan_id)
    
    assert result is not None
    assert result.id == plan_id
    assert result.name == "Plan Mensual"


def test_get_plan_by_slug():
    """
    ID: PLN-003
    Nombre: Obtener plan por slug
    """
    mock_db = MagicMock()
    slug = "plan-mensual"
    
    mock_plan = MagicMock()
    mock_plan.id = uuid4()
    mock_plan.slug = slug
    mock_plan.name = "Plan Mensual"
    
    with patch('app.services.plan_service.PlanRepository.get_by_slug', return_value=mock_plan):
        result = PlanService.get_plan_by_slug(mock_db, slug)
    
    assert result is not None
    assert result.slug == slug


def test_list_plans():
    """
    ID: PLN-004
    Nombre: Listar planes con filtros
    """
    mock_db = MagicMock()
    
    mock_plans = [
        MagicMock(id=uuid4(), name="Plan 1", is_active=True),
        MagicMock(id=uuid4(), name="Plan 2", is_active=True),
    ]
    
    with patch('app.services.plan_service.PlanRepository.get_all', return_value=mock_plans):
        result = PlanService.list_plans(mock_db, is_active=True, limit=10, offset=0)
    
    assert len(result) == 2


def test_search_plans():
    """
    ID: PLN-005
    Nombre: Buscar planes por término
    """
    mock_db = MagicMock()
    search_term = "mensual"
    
    mock_plans = [
        MagicMock(id=uuid4(), name="Plan Mensual", is_active=True),
    ]
    
    with patch('app.services.plan_service.PlanRepository.search', return_value=mock_plans):
        result = PlanService.search_plans(mock_db, search_term, limit=50)
    
    assert len(result) == 1


def test_update_plan_success():
    """
    ID: PLN-006
    Nombre: Actualizar plan exitosamente
    """
    mock_db = MagicMock()
    plan_id = uuid4()
    
    mock_plan = MagicMock()
    mock_plan.id = plan_id
    mock_plan.name = "Plan Mensual Actualizado"
    mock_plan.price = Decimal('55000.00')
    
    with patch('app.services.plan_service.PlanRepository.update', return_value=mock_plan):
        plan_update = PlanUpdate(
            name="Plan Mensual Actualizado",
            price=Decimal('55000.00')
        )
        
        result = PlanService.update_plan(mock_db, plan_id, plan_update)
    
    assert result is not None
    assert result.name == "Plan Mensual Actualizado"
    assert result.price == Decimal('55000.00')


def test_delete_plan_success():
    """
    ID: PLN-007
    Nombre: Eliminar plan exitosamente (soft delete)
    """
    mock_db = MagicMock()
    plan_id = uuid4()
    
    with patch('app.services.plan_service.PlanRepository.delete', return_value=True):
        result = PlanService.delete_plan(mock_db, plan_id)
    
    assert result is True


# ============================================================================
# ❌ CASOS DE ERROR
# ============================================================================

def test_get_plan_by_id_not_found():
    """
    ID: PLN-008
    Nombre: Obtener plan inexistente
    """
    mock_db = MagicMock()
    plan_id = uuid4()
    
    with patch('app.services.plan_service.PlanRepository.get_by_id', return_value=None):
        result = PlanService.get_plan_by_id(mock_db, plan_id)
    
    assert result is None


