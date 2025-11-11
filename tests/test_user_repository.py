import pytest
from unittest.mock import MagicMock, patch
from app.db.models import UserModel as User
from app.repositories.user_repository import UserRepository

# ==============================
# 🧩 TESTS USER REPOSITORY
# ==============================

def test_create_user_success():
    """
    ID: REPUSR-001
    Nombre: Crear usuario en base de datos
    Tipo: Unitario (Repositorio)
    Precondiciones:
    - Sesión mockeada correctamente.
    Pasos:
    1. Llamar a UserRepository.create con datos válidos.
    Resultado Esperado:
    - Retorna el objeto usuario creado.
    """
    mock_db = MagicMock()
    mock_user = MagicMock()
    with patch("app.repositories.user_repository.UserModel", return_value=mock_user):
        result = UserRepository.create(
            mock_db,
            username="mateo",
            email="mateo@demo.com",
            full_name="Mateo Londoño",
            hashed_password="hashed123",
            role="admin",
            disabled=False
        )
    assert result == mock_user
    mock_db.add.assert_called_once_with(mock_user)
    mock_db.commit.assert_called_once()


def test_get_user_by_username_success():
    """
    ID: REPUSR-002
    Nombre: Obtener usuario existente por username
    Tipo: Unitario (Repositorio)
    """
    mock_db = MagicMock()
    expected = {"username": "mateo"}
    mock_db.query.return_value.filter.return_value.first.return_value = expected

    result = UserRepository.get_by_username(mock_db, "mateo")
    assert result == expected


def test_get_user_by_email_success():
    """
    ID: REPUSR-003
    Nombre: Obtener usuario por email
    Tipo: Unitario (Repositorio)
    """
    mock_db = MagicMock()
    expected = {"email": "mateo@demo.com"}
    mock_db.query.return_value.filter.return_value.first.return_value = expected

    result = UserRepository.get_by_email(mock_db, "mateo@demo.com")
    assert result == expected


def test_update_user_success():
    """
    ID: REPUSR-004
    Nombre: Actualizar usuario existente
    Tipo: Unitario (Repositorio)
    """
    mock_db = MagicMock()
    existing_user = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = existing_user

    result = UserRepository.update(mock_db, "mateo", email="nuevo@demo.com")
    assert result == existing_user
    mock_db.commit.assert_called_once()


def test_update_user_not_found():
    """
    ID: REPUSR-005
    Nombre: Actualizar usuario inexistente
    Tipo: Unitario (Repositorio)
    """
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = UserRepository.update(mock_db, "noexiste", email="test@demo.com")
    assert result is None


def test_delete_user_success():
    """
    ID: REPUSR-006
    Nombre: Eliminar usuario existente
    Tipo: Unitario (Repositorio)
    """
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    result = UserRepository.delete(mock_db, "mateo")
    assert result is True
    mock_db.delete.assert_called_once_with(mock_user)
    mock_db.commit.assert_called_once()


def test_delete_user_not_found():
    """
    ID: REPUSR-007
    Nombre: Eliminar usuario inexistente
    Tipo: Unitario (Repositorio)
    """
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None

    result = UserRepository.delete(mock_db, "noexiste")
    assert result is False
