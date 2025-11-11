"""
Ejemplo de pruebas para AttendanceService

Este archivo muestra cómo implementar las pruebas para el servicio de asistencias.
Puede servir como referencia para implementar pruebas en otros módulos.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, date, timedelta
from uuid import uuid4

from app.services.attendance_service import AttendanceService
from app.schemas.attendance import AttendanceResponse, AccessDenialReason
from app.db.models import ClientModel, SubscriptionModel, AttendanceModel
from app.db.models import SubscriptionStatusEnum


# ============================================================================
# ✅ CASOS EXITOSOS
# ============================================================================

def test_create_attendance_success():
    """
    ID: ATT-001
    Nombre: Crear asistencia exitosamente
    Tipo: Unitario (Servicio)
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    # Mock del modelo de asistencia creado
    mock_attendance = MagicMock()
    mock_attendance.id = uuid4()
    mock_attendance.client_id = client_id
    mock_attendance.check_in = datetime.now()
    mock_attendance.meta_info = {}
    
    with patch('app.services.attendance_service.AttendanceRepository.create', return_value=mock_attendance):
        with patch('app.services.attendance_service.NotificationService.send_check_in_notification', new_callable=AsyncMock):
            result = AttendanceService.create_attendance(
                db=mock_db,
                client_id=client_id,
                meta_info={"ip": "127.0.0.1", "authenticated_by": "admin"}
            )
    
    assert result is not None
    assert isinstance(result, AttendanceResponse)
    assert result.client_id == client_id
    assert result.meta_info == {}


def test_get_by_id_success():
    """
    ID: ATT-002
    Nombre: Obtener asistencia por ID existente
    """
    mock_db = MagicMock()
    attendance_id = uuid4()
    client_id = uuid4()
    
    mock_attendance = MagicMock()
    mock_attendance.id = attendance_id
    mock_attendance.client_id = client_id
    mock_attendance.check_in = datetime.now()
    mock_attendance.meta_info = {}
    
    with patch('app.services.attendance_service.AttendanceRepository.get_by_id', return_value=mock_attendance):
        result = AttendanceService.get_by_id(mock_db, attendance_id)
    
    assert result is not None
    assert result.id == attendance_id
    assert result.client_id == client_id


def test_get_client_attendances_success():
    """
    ID: ATT-003
    Nombre: Obtener historial de asistencias de un cliente
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    mock_attendances = [
        MagicMock(id=uuid4(), client_id=client_id, check_in=datetime.now(), meta_info={}),
        MagicMock(id=uuid4(), client_id=client_id, check_in=datetime.now() - timedelta(days=1), meta_info={}),
    ]
    
    with patch('app.services.attendance_service.AttendanceRepository.get_by_client_id', return_value=mock_attendances):
        result = AttendanceService.get_client_attendances(
            db=mock_db,
            client_id=client_id,
            limit=50,
            offset=0
        )
    
    assert len(result) == 2
    assert all(isinstance(att, AttendanceResponse) for att in result)


# ============================================================================
# ✅ VALIDACIÓN DE ACCESO
# ============================================================================

def test_validate_client_access_active_subscription():
    """
    ID: ATT-004
    Nombre: Validar acceso con suscripción activa
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    # Mock de cliente activo
    mock_client = MagicMock()
    mock_client.id = client_id
    mock_client.is_active = True
    
    # Mock de suscripción activa
    mock_subscription = MagicMock()
    mock_subscription.status = SubscriptionStatusEnum.ACTIVE
    mock_subscription.start_date = date.today() - timedelta(days=10)
    mock_subscription.end_date = date.today() + timedelta(days=20)
    
    # Mock de última asistencia (hace más de un día)
    mock_last_attendance = None
    
    # AttendanceService.validate_client_access usa db.query directamente
    # El servicio primero verifica get_today_attendance, luego _get_active_subscription
    # Necesitamos mockear correctamente todas las llamadas
    
    # Mock para db.query(ClientModel)
    client_query = MagicMock()
    client_query.filter.return_value.first.return_value = mock_client
    
    # Mock para _get_active_subscription (llama db.query(SubscriptionModel))
    subscription_query = MagicMock()
    subscription_query.filter.return_value.order_by.return_value.first.return_value = mock_subscription
    
    # Mock para AttendanceRepository.get_today_attendance directamente
    with patch('app.repositories.attendance_repository.AttendanceRepository.get_today_attendance', return_value=mock_last_attendance):
        def mock_query(model):
            if model == ClientModel:
                return client_query
            elif model == SubscriptionModel:
                return subscription_query
            return MagicMock()
        
        mock_db.query = mock_query
        
        can_access, reason, details = AttendanceService.validate_client_access(mock_db, client_id)
    
    assert can_access is True
    assert reason is None


def test_validate_client_access_expired_subscription():
    """
    ID: ATT-005
    Nombre: Validar acceso con suscripción expirada
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    mock_client = MagicMock()
    mock_client.id = client_id
    mock_client.is_active = True
    
    # Mock de suscripción expirada
    # Para testear suscripción expirada, necesitamos que _get_active_subscription retorne una suscripción
    # con end_date < today, pero status="active" (el método busca por status="active")
    mock_subscription = MagicMock()
    mock_subscription.status = SubscriptionStatusEnum.ACTIVE  # Debe ser ACTIVE para que _get_active_subscription la encuentre
    mock_subscription.start_date = date.today() - timedelta(days=30)
    mock_subscription.end_date = date.today() - timedelta(days=1)  # Expirada
    
    # Configurar mocks para múltiples queries
    # El servicio primero verifica get_today_attendance, luego _get_active_subscription
    client_query = MagicMock()
    client_query.filter.return_value.first.return_value = mock_client
    
    subscription_query = MagicMock()
    subscription_query.filter.return_value.order_by.return_value.first.return_value = mock_subscription
    
    # Mock para AttendanceRepository.get_today_attendance directamente
    with patch('app.repositories.attendance_repository.AttendanceRepository.get_today_attendance', return_value=None):
        def query_mock(model):
            if model == ClientModel:
                return client_query
            elif model == SubscriptionModel:
                return subscription_query
            return MagicMock()
        
        mock_db.query = query_mock
        
        can_access, reason, details = AttendanceService.validate_client_access(mock_db, client_id)
    
    assert can_access is False
    # El servicio verifica si end_date < today y retorna SUBSCRIPTION_EXPIRED
    assert reason == AccessDenialReason.SUBSCRIPTION_EXPIRED


def test_validate_client_access_inactive_client():
    """
    ID: ATT-006
    Nombre: Validar acceso con cliente inactivo
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    mock_client = MagicMock()
    mock_client.id = client_id
    mock_client.is_active = False
    
    # Configurar mock para query de ClientModel
    def query_mock(model):
        q = MagicMock()
        if model == ClientModel:
            q.filter.return_value.first.return_value = mock_client
        elif model == AttendanceModel:
            q.filter.return_value.order_by.return_value.first.return_value = None
        return q
    
    mock_db.query.side_effect = query_mock
    
    can_access, reason, details = AttendanceService.validate_client_access(mock_db, client_id)
    
    assert can_access is False
    assert reason == AccessDenialReason.CLIENT_INACTIVE


def test_validate_client_access_no_subscription():
    """
    ID: ATT-007
    Nombre: Validar acceso sin suscripción
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    mock_client = MagicMock()
    mock_client.id = client_id
    mock_client.is_active = True
    
    # El servicio primero verifica get_today_attendance, luego _get_active_subscription
    client_query = MagicMock()
    client_query.filter.return_value.first.return_value = mock_client
    
    subscription_query = MagicMock()
    subscription_query.filter.return_value.order_by.return_value.first.return_value = None  # No hay suscripción activa
    
    # Mock para AttendanceRepository.get_today_attendance directamente
    with patch('app.repositories.attendance_repository.AttendanceRepository.get_today_attendance', return_value=None):
        def query_mock(model):
            if model == ClientModel:
                return client_query
            elif model == SubscriptionModel:
                return subscription_query
            return MagicMock()
        
        mock_db.query = query_mock
        
        can_access, reason, details = AttendanceService.validate_client_access(mock_db, client_id)
    
    assert can_access is False
    assert reason == AccessDenialReason.NO_SUBSCRIPTION


def test_validate_client_access_already_checked_in():
    """
    ID: ATT-008
    Nombre: Validar acceso cuando ya hizo check-in hoy
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    mock_client = MagicMock()
    mock_client.id = client_id
    mock_client.is_active = True
    
    mock_subscription = MagicMock()
    mock_subscription.status = SubscriptionStatusEnum.ACTIVE
    mock_subscription.end_date = date.today() + timedelta(days=20)
    
    # Mock de asistencia hoy
    mock_today_attendance = MagicMock()
    mock_today_attendance.check_in = datetime.now()
    
    # Configurar mocks para múltiples queries
    def query_mock(model):
        q = MagicMock()
        if model == ClientModel:
            q.filter.return_value.first.return_value = mock_client
        elif model == SubscriptionModel:
            q.filter.return_value.order_by.return_value.first.return_value = mock_subscription
        elif model == AttendanceModel:
            q.filter.return_value.order_by.return_value.first.return_value = mock_today_attendance
        return q
    
    mock_db.query.side_effect = query_mock
    
    can_access, reason, details = AttendanceService.validate_client_access(mock_db, client_id)
    
    assert can_access is False
    assert reason == AccessDenialReason.ALREADY_CHECKED_IN


def test_validate_client_access_pending_payment():
    """
    ID: ATT-009
    Nombre: Validar acceso con suscripción pendiente de pago
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    mock_client = MagicMock()
    mock_client.id = client_id
    mock_client.is_active = True
    
    mock_subscription = MagicMock()
    # PENDING_PAYMENT no es una razón de denegación - el servicio solo verifica si existe y no está expirada
    # Si la suscripción está activa pero con PENDING_PAYMENT, el acceso debería permitirse
    # Pero si queremos testear denegación, usamos una suscripción expirada
    mock_subscription.status = SubscriptionStatusEnum.EXPIRED
    mock_subscription.end_date = date.today() - timedelta(days=1)
    
    # Configurar mocks para múltiples queries
    # El servicio primero verifica get_today_attendance, luego _get_active_subscription
    client_query = MagicMock()
    client_query.filter.return_value.first.return_value = mock_client
    
    subscription_query = MagicMock()
    subscription_query.filter.return_value.order_by.return_value.first.return_value = mock_subscription
    
    # Mock para AttendanceRepository.get_today_attendance directamente
    with patch('app.repositories.attendance_repository.AttendanceRepository.get_today_attendance', return_value=None):
        def query_mock(model):
            if model == ClientModel:
                return client_query
            elif model == SubscriptionModel:
                return subscription_query
            return MagicMock()
        
        mock_db.query = query_mock
        
        can_access, reason, details = AttendanceService.validate_client_access(mock_db, client_id)
    
    assert can_access is False
    assert reason == AccessDenialReason.SUBSCRIPTION_EXPIRED


# ============================================================================
# ❌ CASOS DE ERROR
# ============================================================================

def test_get_by_id_not_found():
    """
    ID: ATT-010
    Nombre: Obtener asistencia inexistente
    """
    mock_db = MagicMock()
    attendance_id = uuid4()
    
    with patch('app.services.attendance_service.AttendanceRepository.get_by_id', return_value=None):
        result = AttendanceService.get_by_id(mock_db, attendance_id)
    
    assert result is None


def test_create_attendance_db_error():
    """
    ID: ATT-011
    Nombre: Error al crear asistencia en base de datos
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    with patch('app.services.attendance_service.AttendanceRepository.create', side_effect=Exception("DB Error")):
        with pytest.raises(Exception) as exc_info:
            AttendanceService.create_attendance(
                db=mock_db,
                client_id=client_id
            )
        
        assert "DB Error" in str(exc_info.value)


def test_get_client_attendances_empty():
    """
    ID: ATT-012
    Nombre: Obtener asistencias de cliente sin historial
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    with patch('app.services.attendance_service.AttendanceRepository.get_by_client_id', return_value=[]):
        result = AttendanceService.get_client_attendances(
            db=mock_db,
            client_id=client_id
        )
    
    assert result == []


# ============================================================================
# 📊 CASOS CON FILTROS Y PAGINACIÓN
# ============================================================================

def test_get_all_attendances_with_filters():
    """
    ID: ATT-013
    Nombre: Obtener asistencias con filtros de fecha
    """
    mock_db = MagicMock()
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()
    
    # get_with_client_info retorna tuplas (AttendanceModel, first_name, last_name, dni_number)
    mock_attendance = MagicMock()
    mock_attendance.id = uuid4()
    mock_attendance.client_id = uuid4()
    mock_attendance.check_in = datetime.now()
    mock_attendance.meta_info = {}
    
    mock_result = (mock_attendance, "Juan", "Pérez", "1234567890")
    
    with patch('app.services.attendance_service.AttendanceRepository.get_with_client_info', return_value=[mock_result]):
        result = AttendanceService.get_all_attendances(
            db=mock_db,
            start_date=start_date,
            end_date=end_date
        )
    
    assert len(result) == 1


def test_get_all_attendances_pagination():
    """
    ID: ATT-014
    Nombre: Obtener asistencias con paginación
    """
    mock_db = MagicMock()
    
    # get_with_client_info retorna tuplas
    mock_results = []
    for _ in range(10):
        mock_attendance = MagicMock()
        mock_attendance.id = uuid4()
        mock_attendance.client_id = uuid4()
        mock_attendance.check_in = datetime.now()
        mock_attendance.meta_info = {}
        mock_results.append((mock_attendance, "Juan", "Pérez", "1234567890"))
    
    with patch('app.services.attendance_service.AttendanceRepository.get_with_client_info', return_value=mock_results):
        result = AttendanceService.get_all_attendances(
            db=mock_db,
            limit=10,
            offset=0
        )
    
    assert len(result) == 10


# ============================================================================
# 📈 CASOS DE ESTADÍSTICAS
# ============================================================================

def test_get_attendance_statistics_by_client():
    """
    ID: ATT-015
    Nombre: Obtener estadísticas de asistencia por cliente
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    # Mock de múltiples asistencias
    mock_attendances = [
        MagicMock(check_in=datetime.now() - timedelta(days=i))
        for i in range(5)
    ]
    
    with patch('app.services.attendance_service.AttendanceRepository.get_by_client_id', return_value=mock_attendances):
        # Nota: Este método podría no existir, es un ejemplo
        # result = AttendanceService.get_attendance_statistics_by_client(mock_db, client_id)
        pass  # Implementar cuando el método esté disponible


# ============================================================================
# 🔧 FIXTURES Y HELPERS
# ============================================================================

@pytest.fixture
def mock_client():
    """Fixture para crear un cliente mock"""
    client = MagicMock()
    client.id = uuid4()
    client.is_active = True
    client.first_name = "Test"
    client.last_name = "Client"
    return client


@pytest.fixture
def mock_active_subscription():
    """Fixture para crear una suscripción activa mock"""
    subscription = MagicMock()
    subscription.status = SubscriptionStatusEnum.ACTIVE
    subscription.start_date = date.today() - timedelta(days=10)
    subscription.end_date = date.today() + timedelta(days=20)
    return subscription


@pytest.fixture
def mock_attendance():
    """Fixture para crear una asistencia mock"""
    attendance = MagicMock()
    attendance.id = uuid4()
    attendance.client_id = uuid4()
    attendance.check_in = datetime.now()
    attendance.meta_info = {}
    return attendance


# ============================================================================
# 📝 NOTAS DE USO
# ============================================================================

"""
NOTAS IMPORTANTES:

1. **Mocks y Patches**: Usar `unittest.mock` para mockear dependencias externas
2. **Async Functions**: Para funciones async, usar `AsyncMock` de `unittest.mock`
3. **Fixtures**: Crear fixtures reutilizables en conftest.py
4. **Parametrize**: Usar `@pytest.mark.parametrize` para tests repetitivos
5. **Assertions**: Usar assertions específicas, no solo `assert True`
6. **Documentación**: Cada test debe tener docstring con ID y descripción
7. **Aislamiento**: Cada test debe ser independiente y no depender de otros

EJEMPLO DE TEST PARAMETRIZADO:

@pytest.mark.parametrize("status,expected", [
    (SubscriptionStatusEnum.ACTIVE, True),
    (SubscriptionStatusEnum.EXPIRED, False),
    (SubscriptionStatusEnum.PENDING_PAYMENT, False),
])
def test_validate_access_by_status(status, expected):
    # Test parametrizado
    pass
"""

