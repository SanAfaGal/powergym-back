import pytest
from unittest.mock import MagicMock, patch
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.db.models import UserRoleEnum
from app.schemas.user import UserCreate, UserUpdate


def test_create_user_success():
    """
    ID: SRVUSR-001
    Nombre: Crear usuario exitosamente
    Tipo: Unitario (Servicio)
    Precondiciones:
    - Repositorio mockeado correctamente.
    Pasos:
    1. Llamar a UserService.create_user con datos válidos.
    Resultado Esperado:
    - Retorna el usuario creado.
    """
    mock_db = MagicMock()
    
    # Mock del modelo retornado
    mock_user_model = MagicMock()
    mock_user_model.id = "uuid-1"
    mock_user_model.username = "mateo"
    mock_user_model.email = "mateo@demo.com"
    mock_user_model.full_name = "Mateo Londoño"
    mock_user_model.role = UserRoleEnum.ADMIN  # Enum directo, no MagicMock
    mock_user_model.disabled = False
    mock_user_model.hashed_password = "hashed123"
    
    with patch("app.services.user_service.UserRepository.create", return_value=mock_user_model):
        with patch("app.services.user_service.get_password_hash", return_value="hashed123"):
            user_data = UserCreate(
                username="mateo",
                email="mateo@demo.com",
                password="1234",
                full_name="Mateo Londoño",
                role="admin"
            )
            result = UserService.create_user(mock_db, user_data)

    assert result is not None
    assert result.username == "mateo"


def test_create_user_failure():
    """
    ID: SRVUSR-002
    Nombre: Fallo al crear usuario
    Tipo: Unitario (Servicio)
    """
    mock_db = MagicMock()
    
    with patch("app.services.user_service.UserRepository.create", side_effect=Exception("DB Error")):
        with patch("app.services.user_service.get_password_hash", return_value="hashed"):
            user_data = UserCreate(
                username="error",
                email="error@demo.com",
                password="1234",
                full_name="Error User",
                role="admin"
            )
            
            with pytest.raises(Exception) as exc_info:
                UserService.create_user(mock_db, user_data)
            
            assert "DB Error" in str(exc_info.value)


def test_get_user_by_username_success():
    """
    ID: SRVUSR-003
    Nombre: Obtener usuario por username
    Tipo: Unitario (Servicio)
    """
    mock_db = MagicMock()
    
    mock_user_model = MagicMock()
    mock_user_model.username = "mateo"
    mock_user_model.email = "mateo@demo.com"
    mock_user_model.full_name = "Mateo Londoño"
    mock_user_model.role = UserRoleEnum.ADMIN  # Enum directo
    mock_user_model.disabled = False
    mock_user_model.hashed_password = "hashed"

    with patch("app.services.user_service.UserRepository.get_by_username", return_value=mock_user_model):
        result = UserService.get_user_by_username(mock_db, "mateo")

    assert result is not None
    assert result.username == "mateo"
    assert result.email == "mateo@demo.com"


def test_get_user_by_email_success():
    """
    ID: SRVUSR-004
    Nombre: Obtener usuario por email
    Tipo: Unitario (Servicio)
    """
    mock_db = MagicMock()
    
    mock_user_model = MagicMock()
    mock_user_model.username = "mateo"
    mock_user_model.email = "mateo@demo.com"
    mock_user_model.full_name = "Mateo Londoño"
    mock_user_model.role = UserRoleEnum.ADMIN  # Enum directo
    mock_user_model.disabled = False
    mock_user_model.hashed_password = "hashed"

    with patch("app.services.user_service.UserRepository.get_by_email", return_value=mock_user_model):
        result = UserService.get_user_by_email(mock_db, "mateo@demo.com")

    assert result is not None
    assert result.email == "mateo@demo.com"


def test_get_user_not_found():
    """
    ID: SRVUSR-005
    Nombre: Obtener usuario inexistente
    Tipo: Unitario (Servicio)
    """
    mock_db = MagicMock()
    
    with patch("app.services.user_service.UserRepository.get_by_username", return_value=None):
        result = UserService.get_user_by_username(mock_db, "noexiste")

    assert result is None


def test_update_user_success():
    """
    ID: SRVUSR-006
    Nombre: Actualizar usuario exitosamente
    Tipo: Unitario (Servicio)
    """
    mock_db = MagicMock()
    
    mock_user_model = MagicMock()
    mock_user_model.username = "mateo"
    mock_user_model.email = "nuevo@demo.com"
    mock_user_model.full_name = "Mateo Londoño"
    mock_user_model.role = UserRoleEnum.ADMIN  # Enum directo
    mock_user_model.disabled = False
    mock_user_model.hashed_password = "hashed"

    with patch("app.services.user_service.UserRepository.update", return_value=mock_user_model):
        user_update = UserUpdate(email="nuevo@demo.com")
        result = UserService.update_user(mock_db, "mateo", user_update)

    assert result is not None
    assert result.email == "nuevo@demo.com"


def test_update_user_not_found():
    """
    ID: SRVUSR-007
    Nombre: Intentar actualizar usuario inexistente
    Tipo: Unitario (Servicio)
    """
    mock_db = MagicMock()
    
    with patch("app.services.user_service.UserRepository.update", return_value=None):
        user_update = UserUpdate(email="nuevo@demo.com")
        result = UserService.update_user(mock_db, "noexiste", user_update)

    assert result is None


def test_delete_user_success():
    """
    ID: SRVUSR-008
    Nombre: Eliminar usuario exitosamente
    Tipo: Unitario (Servicio)
    """
    mock_db = MagicMock()
    
    with patch("app.services.user_service.UserRepository.delete", return_value=True):
        result = UserService.delete_user(mock_db, "mateo")

    assert result is True


def test_delete_user_not_found():
    """
    ID: SRVUSR-009
    Nombre: Eliminar usuario inexistente
    Tipo: Unitario (Servicio)
    """
    mock_db = MagicMock()
    
    with patch("app.services.user_service.UserRepository.delete", return_value=False):
        result = UserService.delete_user(mock_db, "noexiste")

    assert result is False