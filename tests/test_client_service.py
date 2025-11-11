import pytest
from unittest.mock import MagicMock, patch
from app.services.client_service import ClientService
from app.schemas.client import ClientCreate, ClientUpdate, DocumentType, GenderType
from app.db.models import DocumentTypeEnum, GenderTypeEnum
from datetime import date
from uuid import uuid4


# =====================================================================================
# ✅ CASOS EXITOSOS
# =====================================================================================

def test_create_client_success():
    """
    ID: CLI-001
    Nombre: Crear cliente exitosamente
    Tipo: Unitario (Servicio)
    Precondiciones:
    - El repositorio devuelve un cliente válido al crear.
    Pasos:
    1. Llamar a ClientService.create_client con datos válidos.
    Resultado Esperado:
    - Retorna un objeto Client con datos válidos.
    """
    mock_db = MagicMock()
    
    # Mock del modelo retornado por el repositorio
    mock_client_model = MagicMock()
    mock_client_model.id = uuid4()
    mock_client_model.dni_type = DocumentTypeEnum.CC
    mock_client_model.dni_number = "1234567890"
    mock_client_model.first_name = "Mateo"
    mock_client_model.middle_name = None
    mock_client_model.last_name = "Pérez"
    mock_client_model.second_last_name = None
    mock_client_model.phone = "3001234567"
    mock_client_model.alternative_phone = None
    mock_client_model.birth_date = date(1990, 1, 1)
    mock_client_model.gender = GenderTypeEnum.MALE
    mock_client_model.address = "Calle 123"
    mock_client_model.is_active = True
    mock_client_model.created_at = MagicMock()
    mock_client_model.created_at.isoformat.return_value = "2025-01-01T00:00:00"
    mock_client_model.updated_at = MagicMock()
    mock_client_model.updated_at.isoformat.return_value = "2025-01-01T00:00:00"
    mock_client_model.meta_info = {}  # Debe ser un diccionario vacío

    with patch('app.services.client_service.ClientRepository.create', return_value=mock_client_model):
        client_data = ClientCreate(
            dni_type=DocumentType.CC,
            dni_number="1234567890",
            first_name="Mateo",
            last_name="Pérez",
            phone="3001234567",
            birth_date=date(1990, 1, 1),
            gender=GenderType.M,  # M = "male"
            address="Calle 123"
        )
        
        result = ClientService.create_client(mock_db, client_data)
        
        assert result is not None
        assert result.first_name == "Mateo"
        assert result.dni_number == "1234567890"


def test_get_client_by_id_success():
    """
    ID: CLI-002
    Nombre: Obtener cliente por ID existente
    Tipo: Unitario (Servicio)
    Precondiciones:
    - El cliente existe en la base de datos simulada.
    Pasos:
    1. Llamar a ClientService.get_client_by_id con ID válido.
    Resultado Esperado:
    - Retorna el cliente correspondiente.
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    mock_client_model = MagicMock()
    mock_client_model.id = client_id
    mock_client_model.dni_type = DocumentTypeEnum.CC
    mock_client_model.dni_number = "1234567890"
    mock_client_model.first_name = "Mateo"
    mock_client_model.middle_name = None
    mock_client_model.last_name = "Pérez"
    mock_client_model.second_last_name = None
    mock_client_model.phone = "3001234567"
    mock_client_model.alternative_phone = None
    mock_client_model.birth_date = date(1990, 1, 1)
    mock_client_model.gender = GenderTypeEnum.MALE
    mock_client_model.address = "Calle 123"
    mock_client_model.is_active = True
    mock_client_model.created_at = MagicMock()
    mock_client_model.created_at.isoformat.return_value = "2025-01-01T00:00:00"
    mock_client_model.updated_at = MagicMock()
    mock_client_model.updated_at.isoformat.return_value = "2025-01-01T00:00:00"
    mock_client_model.meta_info = {}  # Debe ser un diccionario vacío

    with patch('app.services.client_service.ClientRepository.get_by_id', return_value=mock_client_model):
        result = ClientService.get_client_by_id(mock_db, client_id)
        
        assert result is not None
        assert result.id == client_id
        assert result.first_name == "Mateo"


def test_update_client_success():
    """
    ID: CLI-003
    Nombre: Actualizar cliente exitosamente
    Tipo: Unitario (Servicio)
    Precondiciones:
    - Cliente existente.
    Pasos:
    1. Llamar a ClientService.update_client con datos válidos.
    Resultado Esperado:
    - Retorna el cliente actualizado.
    """
    mock_db = MagicMock()
    client_id = uuid4()
    
    mock_client_model = MagicMock()
    mock_client_model.id = client_id
    mock_client_model.dni_type = DocumentTypeEnum.CC
    mock_client_model.dni_number = "1234567890"
    mock_client_model.first_name = "Mateo"
    mock_client_model.middle_name = None
    mock_client_model.last_name = "Pérez"
    mock_client_model.second_last_name = None
    mock_client_model.phone = "3009998888"  # Teléfono actualizado
    mock_client_model.alternative_phone = None
    mock_client_model.birth_date = date(1990, 1, 1)
    mock_client_model.gender = GenderTypeEnum.MALE
    mock_client_model.address = "Calle 123"
    mock_client_model.is_active = True
    mock_client_model.created_at = MagicMock()
    mock_client_model.created_at.isoformat.return_value = "2025-01-01T00:00:00"
    mock_client_model.updated_at = MagicMock()
    mock_client_model.updated_at.isoformat.return_value = "2025-01-02T00:00:00"
    mock_client_model.meta_info = {}  # Debe ser un diccionario vacío

    with patch('app.services.client_service.ClientRepository.update', return_value=mock_client_model):
        client_update = ClientUpdate(phone="3009998888")
        result = ClientService.update_client(mock_db, client_id, client_update)
        
        assert result is not None
        assert result.phone == "3009998888"


def test_delete_client_success():
    """
    ID: CLI-004
    Nombre: Eliminar cliente exitosamente
    Tipo: Unitario (Servicio)
    Precondiciones:
    - Cliente existente en el repositorio simulado.
    Pasos:
    1. Llamar a ClientService.delete_client con un ID válido.
    Resultado Esperado:
    - Retorna True.
    """
    mock_db = MagicMock()
    client_id = uuid4()

    with patch('app.services.client_service.ClientRepository.delete', return_value=True):
        result = ClientService.delete_client(mock_db, client_id)
        assert result is True


# =====================================================================================
# ❌ CASOS DE ERROR
# =====================================================================================

def test_create_client_failure():
    """
    ID: CLI-005
    Nombre: Fallo al crear cliente
    Tipo: Unitario (Servicio)
    Precondiciones:
    - El repositorio lanza una excepción.
    Pasos:
    1. Llamar a ClientService.create_client con datos que causen error.
    Resultado Esperado:
    - Lanza una excepción.
    """
    mock_db = MagicMock()

    with patch('app.services.client_service.ClientRepository.create', side_effect=Exception("DB error")):
        client_data = ClientCreate(
            dni_type=DocumentType.CC,
            dni_number="1234567890",
            first_name="Error",
            last_name="Test",
            phone="3001234567",
            birth_date=date(1990, 1, 1),
            gender=GenderType.M,  # M = "male"
            address="Calle 123"
        )
        
        with pytest.raises(Exception) as exc_info:
            ClientService.create_client(mock_db, client_data)
        
        assert "DB error" in str(exc_info.value)


def test_get_client_by_id_not_found():
    """
    ID: CLI-006
    Nombre: Obtener cliente inexistente
    Tipo: Unitario (Servicio)
    Precondiciones:
    - El repositorio devuelve None.
    Pasos:
    1. Llamar a ClientService.get_client_by_id con ID inexistente.
    Resultado Esperado:
    - Retorna None.
    """
    mock_db = MagicMock()
    client_id = uuid4()

    with patch('app.services.client_service.ClientRepository.get_by_id', return_value=None):
        result = ClientService.get_client_by_id(mock_db, client_id)
        assert result is None


def test_update_client_not_found():
    """
    ID: CLI-007
    Nombre: Fallo al actualizar cliente inexistente
    Tipo: Unitario (Servicio)
    Precondiciones:
    - Cliente no existe.
    Pasos:
    1. Llamar a ClientService.update_client con ID inválido.
    Resultado Esperado:
    - Retorna None.
    """
    mock_db = MagicMock()
    client_id = uuid4()

    with patch('app.services.client_service.ClientRepository.update', return_value=None):
        client_update = ClientUpdate(address="Nueva dirección")
        result = ClientService.update_client(mock_db, client_id, client_update)
        
        assert result is None


def test_delete_client_failure():
    """
    ID: CLI-008
    Nombre: Fallo al eliminar cliente
    Tipo: Unitario (Servicio)
    Precondiciones:
    - El repositorio lanza una excepción.
    Pasos:
    1. Llamar a ClientService.delete_client con ID que causa error.
    Resultado Esperado:
    - Lanza una excepción.
    """
    mock_db = MagicMock()
    client_id = uuid4()

    with patch('app.services.client_service.ClientRepository.delete', side_effect=Exception("Delete error")):
        with pytest.raises(Exception) as exc_info:
            ClientService.delete_client(mock_db, client_id)
        
        assert "Delete error" in str(exc_info.value)