"""
Pruebas de integración para API de reconocimiento facial

Este archivo contiene 8 pruebas principales para los endpoints de reconocimiento facial.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from uuid import uuid4
import base64
import numpy as np
from PIL import Image
import io

from main import app
from app.api.dependencies import get_current_user
from app.db.models import UserModel, UserRoleEnum
from app.schemas.user import User


# ============================================================================
# ✅ HELPER FUNCTIONS
# ============================================================================

def create_test_image_base64() -> str:
    """Crear imagen de prueba en Base64"""
    # Crear imagen simple de 100x100 píxeles
    img = Image.new('RGB', (100, 100), color='red')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    img_bytes = buffer.getvalue()
    return base64.b64encode(img_bytes).decode('utf-8')


def get_auth_token(client: TestClient, username: str = "admin", password: str = "admin123"):
    """Obtener token de autenticación"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password}
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


# ============================================================================
# ✅ CASOS EXITOSOS
# ============================================================================

def test_register_face_success():
    """
    ID: API-FACE-001
    Nombre: Registrar rostro exitosamente
    Tipo: Integración (API)
    """
    client = TestClient(app)
    client_id = uuid4()
    image_base64 = create_test_image_base64()
    
    # Mock de autenticación usando dependency_overrides
    mock_user = User(
        username="admin",
        email="admin@test.com",
        full_name="Admin User",
        role=UserRoleEnum.ADMIN,
        disabled=False
    )
    
    # Mock de resultado de registro
    mock_result = {
        "success": True,
        "biometric_id": str(uuid4()),
        "client_id": str(client_id)
    }
    
    # Override dependency
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    try:
        with patch('app.api.v1.endpoints.face_recognition.ClientService.get_client_by_id', return_value=MagicMock(is_active=True)):
            with patch('app.api.v1.endpoints.face_recognition.FaceRecognitionService.register_face', return_value=mock_result):
                response = client.post(
                    "/api/v1/face/register",
                    json={"client_id": str(client_id), "image_base64": image_base64}
                )
        
        assert response.status_code == 201 or response.status_code == 200
        assert response.json()["success"] is True
    finally:
        app.dependency_overrides.clear()


def test_authenticate_face_success():
    """
    ID: API-FACE-002
    Nombre: Autenticar rostro exitosamente
    """
    client = TestClient(app)
    image_base64 = create_test_image_base64()
    
    mock_user = User(
        username="admin",
        email="admin@test.com",
        full_name="Admin User",
        role=UserRoleEnum.ADMIN,
        disabled=False
    )
    
    mock_result = {
        "success": True,
        "client_id": str(uuid4()),
        "client_info": {
            "first_name": "Juan",
            "last_name": "Pérez"
        },
        "confidence": 0.95
    }
    
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    try:
        with patch('app.api.v1.endpoints.face_recognition.FaceRecognitionService.authenticate_face', return_value=mock_result):
            response = client.post(
                "/api/v1/face/authenticate",
                json={"image_base64": image_base64}
            )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "client_id" in response.json()
    finally:
        app.dependency_overrides.clear()


def test_compare_faces_success():
    """
    ID: API-FACE-003
    Nombre: Comparar dos rostros exitosamente
    """
    client = TestClient(app)
    image1_base64 = create_test_image_base64()
    image2_base64 = create_test_image_base64()
    
    mock_user = User(
        username="admin",
        email="admin@test.com",
        full_name="Admin User",
        role=UserRoleEnum.ADMIN,
        disabled=False
    )
    
    mock_result = {
        "success": True,
        "match": True,
        "confidence": 0.85,
        "distance": 0.15
    }
    
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    try:
        with patch('app.api.v1.endpoints.face_recognition.FaceRecognitionService.compare_two_faces', return_value=mock_result):
            response = client.post(
                "/api/v1/face/compare",
                json={
                    "image_base64_1": image1_base64,
                    "image_base64_2": image2_base64
                }
            )
        
        assert response.status_code == 200
        assert response.json()["match"] is True
    finally:
        app.dependency_overrides.clear()


def test_delete_face_success():
    """
    ID: API-FACE-004
    Nombre: Eliminar datos biométricos exitosamente
    """
    client = TestClient(app)
    client_id = uuid4()
    
    mock_user = User(
        username="admin",
        email="admin@test.com",
        full_name="Admin User",
        role=UserRoleEnum.ADMIN,
        disabled=False
    )
    
    mock_result = {
        "success": True,
        "message": "Face biometric deactivated successfully"
    }
    
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    try:
        with patch('app.api.v1.endpoints.face_recognition.ClientService.get_client_by_id', return_value=MagicMock(is_active=True)):
            with patch('app.api.v1.endpoints.face_recognition.FaceRecognitionService.delete_face', return_value=mock_result):
                response = client.delete(
                    f"/api/v1/face/{client_id}"
                )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
    finally:
        app.dependency_overrides.clear()


# ============================================================================
# ❌ CASOS DE ERROR
# ============================================================================

def test_register_face_invalid_image():
    """
    ID: API-FACE-005
    Nombre: Error al registrar rostro con imagen inválida
    """
    client = TestClient(app)
    client_id = uuid4()
    
    mock_user = User(
        username="admin",
        email="admin@test.com",
        full_name="Admin User",
        role=UserRoleEnum.ADMIN,
        disabled=False
    )
    
    mock_result = {
        "success": False,
        "error": "No face detected in the image"
    }
    
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    try:
        with patch('app.api.v1.endpoints.face_recognition.ClientService.get_client_by_id', return_value=MagicMock(is_active=True)):
            with patch('app.api.v1.endpoints.face_recognition.FaceRecognitionService.register_face', return_value=mock_result):
                response = client.post(
                    "/api/v1/face/register",
                    json={"client_id": str(client_id), "image_base64": "invalid_base64_string"}
                )
        
        assert response.status_code == 400
        assert "error" in response.json()
    finally:
        app.dependency_overrides.clear()


def test_authenticate_face_not_found():
    """
    ID: API-FACE-006
    Nombre: Error al autenticar rostro no encontrado
    """
    client = TestClient(app)
    image_base64 = create_test_image_base64()
    
    mock_user = MagicMock()
    mock_user.username = "admin"
    
    mock_result = {
        "success": False,
        "error": "No matching face found"
    }
    
    with patch('app.api.v1.endpoints.face_recognition.get_current_user', return_value=mock_user):
        with patch('app.api.v1.endpoints.face_recognition.FaceRecognitionService.authenticate_face', return_value=mock_result):
            response = client.post(
                "/api/v1/face/authenticate",
                json={"image_base64": image_base64},
                headers={"Authorization": f"Bearer fake_token"}
            )
    
    assert response.status_code == 401
    assert "error" in response.json()


def test_register_face_unauthorized():
    """
    ID: API-FACE-007
    Nombre: Error al registrar rostro sin autenticación
    """
    client = TestClient(app)
    client_id = uuid4()
    image_base64 = create_test_image_base64()
    
    # Sin dependency override, debería fallar con 401
    response = client.post(
        "/api/v1/face/register",
        json={"client_id": str(client_id), "image_base64": image_base64}
        # Sin header de autorización
    )
    
    # Debe retornar 401 sin autenticación
    assert response.status_code == 401


def test_compare_faces_invalid_input():
    """
    ID: API-FACE-008
    Nombre: Error al comparar rostros con entrada inválida
    """
    client = TestClient(app)
    
    mock_user = User(
        username="admin",
        email="admin@test.com",
        full_name="Admin User",
        role=UserRoleEnum.ADMIN,
        disabled=False
    )
    
    mock_result = {
        "success": False,
        "error": "Failed to parse embeddings for comparison"
    }
    
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    try:
        with patch('app.api.v1.endpoints.face_recognition.FaceRecognitionService.compare_two_faces', return_value=mock_result):
            response = client.post(
                "/api/v1/face/compare",
                json={
                    "image_base64_1": "invalid",
                    "image_base64_2": "invalid"
                }
            )
        
        assert response.status_code == 400
        assert "error" in response.json()
    finally:
        app.dependency_overrides.clear()

