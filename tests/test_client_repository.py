import pytest
from unittest.mock import MagicMock, patch
from app.db.models import ClientModel, DocumentTypeEnum, GenderTypeEnum
from app.repositories.client_repository import ClientRepository
from datetime import date
from uuid import uuid4


# ==============================
# 🧩 TESTS CLIENT REPOSITORY
# ==============================

def test_create_client_success():
    """
    ID: REPCLI-001
    Nombre: Crear cliente en base de datos
    Tipo: Unitario (Repositorio)
    """
    mock_db = MagicMock()
    mock_client = MagicMock()
    
    with patch("app.repositories.client_repository.ClientModel", return_value=mock_client):
        result = ClientRepository.create(
            db=mock_db,
            dni_type=DocumentTypeEnum.CC,
            dni_number="1234567890",
            first_name="Juan",
            middle_name=None,
            last_name="Pérez",
            second_last_name=None,
            phone="3001234567",
            alternative_phone=None,
            birth_date=date(1990, 1, 1),
            gender=GenderTypeEnum.MALE,
            address="Calle 123"
        )
    
    assert result == mock_client
    mock_db.add.assert_called_once_with(mock_client)
    mock_db.commit.assert_called_once()


def test_get_client_by_id_success():
    """
    ID: REPCLI-002
    Nombre: Obtener cliente existente por ID
    Tipo: Unitario (Repositorio)
    """
    mock_db = MagicMock()
    client_id = uuid4()
    expected = MagicMock()
    expected.id = client_id
    expected.first_name = "Juan"
    
    # Mock para SQLAlchemy 2.0: db.execute().scalars().first()
    mock_db.execute.return_value.scalars.return_value.first.return_value = expected

    result = ClientRepository.get_by_id(mock_db, client_id)
    assert result == expected


def test_update_client_success():
    """
    ID: REPCLI-003
    Nombre: Actualizar cliente existente
    Tipo: Unitario (Repositorio)
    """
    mock_db = MagicMock()
    client_id = uuid4()
    existing_client = MagicMock()
    existing_client.first_name = "Juan"
    
    # Mock para encontrar el cliente existente
    mock_db.execute.return_value.scalars.return_value.first.return_value = existing_client

    # ClientRepository.update usa kwargs, no un diccionario
    result = ClientRepository.update(mock_db, client_id, first_name="Nuevo")
    
    # El método debería retornar el cliente actualizado
    assert result is not None
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(existing_client)


def test_update_client_not_found():
    """
    ID: REPCLI-004
    Nombre: Intentar actualizar cliente inexistente
    Tipo: Unitario (Repositorio)
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    # Mock para cliente no encontrado
    mock_db.execute.return_value.scalars.return_value.first.return_value = None

    result = ClientRepository.update(mock_db, client_id, first_name="Test")
    assert result is None


def test_delete_client_success():
    """
    ID: REPCLI-005
    Nombre: Eliminar cliente existente
    Tipo: Unitario (Repositorio)
    """
    mock_db = MagicMock()
    client_id = uuid4()
    mock_client = MagicMock()
    
    # Mock para encontrar el cliente
    mock_db.execute.return_value.scalars.return_value.first.return_value = mock_client

    result = ClientRepository.delete(mock_db, client_id)
    
    assert result is True
    # Verificar que se hizo commit (el método delete puede no llamar a db.delete explícitamente)
    mock_db.commit.assert_called_once()


def test_delete_client_not_found():
    """
    ID: REPCLI-006
    Nombre: Eliminar cliente inexistente
    Tipo: Unitario (Repositorio)
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    # Mock para cliente no encontrado
    mock_db.execute.return_value.scalars.return_value.first.return_value = None

    result = ClientRepository.delete(mock_db, client_id)
    assert result is False