"""
Pruebas para AttendanceRepository

Este archivo contiene 8 pruebas principales para el repositorio de asistencias.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from uuid import uuid4

from app.repositories.attendance_repository import AttendanceRepository
from app.db.models import AttendanceModel


# ============================================================================
# ✅ CASOS EXITOSOS
# ============================================================================

def test_create_attendance():
    """
    ID: REPATT-001
    Nombre: Crear registro de asistencia en base de datos
    Tipo: Unitario (Repositorio)
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    mock_attendance = MagicMock()
    mock_attendance.id = uuid4()
    mock_attendance.client_id = client_id
    mock_attendance.check_in = datetime.now()
    mock_attendance.meta_info = {}
    
    with patch('app.repositories.attendance_repository.AttendanceModel', return_value=mock_attendance):
        result = AttendanceRepository.create(
            db=mock_db,
            client_id=client_id,
            meta_info={"ip": "127.0.0.1"}
        )
    
    assert result == mock_attendance
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_get_by_id_success():
    """
    ID: REPATT-002
    Nombre: Obtener asistencia existente por ID
    """
    mock_db = MagicMock()
    attendance_id = uuid4()
    
    expected = MagicMock()
    expected.id = attendance_id
    expected.client_id = uuid4()
    expected.check_in = datetime.now()
    
    # Mock para SQLAlchemy 1.x: db.query().filter().first()
    mock_db.query.return_value.filter.return_value.first.return_value = expected
    
    result = AttendanceRepository.get_by_id(mock_db, attendance_id)
    
    assert result is not None
    assert result.id == attendance_id


def test_get_by_client_id():
    """
    ID: REPATT-003
    Nombre: Obtener asistencias de un cliente con paginación
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    expected_attendances = [
        MagicMock(id=uuid4(), client_id=client_id, check_in=datetime.now()),
        MagicMock(id=uuid4(), client_id=client_id, check_in=datetime.now() - timedelta(days=1)),
    ]
    
    mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = expected_attendances
    
    result = AttendanceRepository.get_by_client_id(mock_db, client_id, limit=10, offset=0)
    
    assert len(result) == 2
    assert all(att.client_id == client_id for att in result)


def test_get_with_client_info():
    """
    ID: REPATT-004
    Nombre: Obtener asistencias con información del cliente
    """
    mock_db = MagicMock()
    
    # get_with_client_info retorna tuplas (AttendanceModel, first_name, last_name, dni_number)
    mock_attendance = MagicMock()
    mock_attendance.id = uuid4()
    mock_result = (mock_attendance, "Juan", "Pérez", "1234567890")
    
    # El query real tiene múltiples filtros, necesitamos mockear toda la cadena
    query_mock = MagicMock()
    query_mock.join.return_value = query_mock
    query_mock.filter.return_value = query_mock
    query_mock.order_by.return_value = query_mock
    query_mock.offset.return_value = query_mock
    query_mock.limit.return_value = query_mock
    query_mock.all.return_value = [mock_result]
    mock_db.query.return_value = query_mock
    
    result = AttendanceRepository.get_with_client_info(
        db=mock_db,
        limit=10,
        offset=0
    )
    
    assert len(result) == 1


def test_get_with_client_info_filtered_by_date():
    """
    ID: REPATT-005
    Nombre: Obtener asistencias filtradas por rango de fechas
    """
    mock_db = MagicMock()
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()
    
    mock_attendance = MagicMock()
    mock_attendance.check_in = datetime.now() - timedelta(days=3)
    mock_result = (mock_attendance, "Juan", "Pérez", "1234567890")
    
    # El query real tiene múltiples filtros cuando hay fechas
    query_mock = MagicMock()
    query_mock.join.return_value = query_mock
    query_mock.filter.return_value = query_mock
    query_mock.order_by.return_value = query_mock
    query_mock.offset.return_value = query_mock
    query_mock.limit.return_value = query_mock
    query_mock.all.return_value = [mock_result]
    mock_db.query.return_value = query_mock
    
    result = AttendanceRepository.get_with_client_info(
        db=mock_db,
        start_date=start_date,
        end_date=end_date,
        limit=10,
        offset=0
    )
    
    assert len(result) == 1


def test_get_latest_by_client_id_today():
    """
    ID: REPATT-006
    Nombre: Obtener última asistencia de hoy de un cliente
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    mock_attendance = MagicMock()
    mock_attendance.id = uuid4()
    mock_attendance.client_id = client_id
    mock_attendance.check_in = datetime.now()
    
    # El método real se llama get_today_attendance
    query_mock = MagicMock()
    query_mock.filter.return_value = query_mock
    query_mock.order_by.return_value = query_mock
    query_mock.first.return_value = mock_attendance
    mock_db.query.return_value = query_mock
    
    result = AttendanceRepository.get_today_attendance(mock_db, client_id)
    
    assert result is not None
    assert result.client_id == client_id


def test_count_by_client_id():
    """
    ID: REPATT-007
    Nombre: Contar asistencias de un cliente (usando get_by_client_id)
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    # No existe count_by_client_id, usar get_by_client_id y len
    mock_attendances = [MagicMock() for _ in range(15)]
    mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_attendances
    
    result = AttendanceRepository.get_by_client_id(mock_db, client_id, limit=1000, offset=0)
    
    assert len(result) == 15


# ============================================================================
# ❌ CASOS DE ERROR
# ============================================================================

def test_get_by_id_not_found():
    """
    ID: REPATT-008
    Nombre: Obtener asistencia inexistente
    """
    mock_db = MagicMock()
    attendance_id = uuid4()
    
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    result = AttendanceRepository.get_by_id(mock_db, attendance_id)
    
    assert result is None

