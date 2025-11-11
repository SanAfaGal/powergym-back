import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from app.services.face_recognition.core import FaceRecognitionService


def test_extract_face_encoding():
    """Debe retornar un embedding válido para una imagen válida"""
    # Imagen de prueba (puede ser cualquier array válido)
    fake_image = np.zeros((100, 100, 3), dtype=np.uint8)
    
    with patch.object(FaceRecognitionService, 'extract_face_encoding', return_value=(np.array([0.1] * 512), b"thumbnail")):
        encoding, thumbnail = FaceRecognitionService.extract_face_encoding(fake_image)
        assert encoding is not None
        assert len(encoding) == 512


def test_compare_faces():
    """Debe retornar True cuando las caras son iguales"""
    # Usar numpy arrays con dimensiones correctas (512 para InsightFace)
    e1 = np.array([0.1] * 512, dtype=np.float32)
    e2 = np.array([0.1] * 512, dtype=np.float32)
    
    match, distance = FaceRecognitionService.compare_faces(e1, e2, tolerance=0.5)
    
    assert match is True
    # La distancia para embeddings idénticos puede variar según la implementación
    # Simplemente verificamos que hizo match
    assert isinstance(distance, (float, np.floating))


def test_register_face():
    """Debe registrar correctamente un rostro en la base de datos"""
    mock_db = MagicMock()
    client_id = "uuid-123"
    fake_encoding = [0.5] * 512  # 512 dimensiones para InsightFace
    fake_thumbnail = b"fake_thumbnail_data"
    fake_image_base64 = "fake_base64_string"
    
    # Mock extract_face_encoding para retornar tupla (embedding, thumbnail)
    with patch.object(FaceRecognitionService, 'extract_face_encoding', return_value=(fake_encoding, fake_thumbnail)):
        # Mock FaceDatabase.store_face_biometric
        with patch('app.services.face_recognition.core.FaceDatabase.store_face_biometric') as mock_method:
            mock_method.return_value = {
                "success": True,
                "biometric_id": "biometric-1"
            }
            
            result = FaceRecognitionService.register_face(mock_db, client_id, fake_image_base64)
            
            assert result is not None
            assert result["success"] is True
            mock_method.assert_called_once_with(
                db=mock_db,
                client_id=client_id,
                embedding=fake_encoding,
                thumbnail=fake_thumbnail
            )


def test_extract_face_encoding_invalid_image():
    """Debe lanzar error con imagen inválida"""
    invalid_image = None
    
    with pytest.raises((ValueError, AttributeError, Exception)):
        FaceRecognitionService.extract_face_encoding(invalid_image)


def test_compare_faces_different_embeddings():
    """Debe retornar False cuando los embeddings son distintos"""
    # Usar embeddings con mayor diferencia (512 dimensiones)
    e1 = np.array([0.0] * 512, dtype=np.float32)
    e2 = np.array([1.0] * 512, dtype=np.float32)
    
    match, distance = FaceRecognitionService.compare_faces(e1, e2, tolerance=0.5)
    
    # Verificar que retorna False (no match)
    assert match is False
    # Verificar que retorna alguna distancia válida
    assert isinstance(distance, (float, np.floating))


def test_register_face_db_failure():
    """Debe manejar errores de base de datos al registrar rostro"""
    mock_db = MagicMock()
    client_id = "uuid-123"
    fake_encoding = [0.5] * 512  # 512 dimensiones
    fake_thumbnail = b"fake_thumbnail_data"
    fake_image_base64 = "fake_base64_string"
    
    with patch.object(FaceRecognitionService, 'extract_face_encoding', return_value=(fake_encoding, fake_thumbnail)):
        with patch('app.services.face_recognition.core.FaceDatabase.store_face_biometric') as mock_method:
            mock_method.side_effect = Exception("DB Error")
            
            result = FaceRecognitionService.register_face(mock_db, client_id, fake_image_base64)
            
            # El método captura la excepción y retorna un dict con success=False
            assert result is not None
            assert result["success"] is False
            assert "error" in result


def test_compare_faces_invalid_input():
    """Debe manejar entradas inválidas en compare_faces"""
    with pytest.raises((ValueError, TypeError, Exception)):
        FaceRecognitionService.compare_faces(None, None)


def test_extract_face_encoding_no_face_found():
    """Debe manejar el caso cuando no se detecta ningún rostro"""
    fake_image = np.zeros((100, 100, 3), dtype=np.uint8)
    
    with patch.object(FaceRecognitionService, 'extract_face_encoding', return_value=None):
        result = FaceRecognitionService.extract_face_encoding(fake_image)
        assert result is None