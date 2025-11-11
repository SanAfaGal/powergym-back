"""
Pruebas para EmbeddingService

Este archivo contiene 8 pruebas principales para el servicio de embeddings faciales.
"""

import pytest
import numpy as np
from unittest.mock import MagicMock, patch, Mock
from app.services.face_recognition.embedding import EmbeddingService
from app.core.config import settings


# ============================================================================
# ✅ CASOS EXITOSOS
# ============================================================================

def test_extract_face_encoding_valid_image():
    """
    ID: EMB-001
    Nombre: Extraer embedding de imagen válida con rostro
    Tipo: Unitario (Servicio)
    """
    # Crear imagen mock con un rostro
    mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    # Mock de FaceAnalysis
    mock_face = Mock()
    mock_face.normed_embedding = np.random.rand(512).astype(np.float64)
    mock_face.bbox = np.array([10, 10, 90, 90])
    
    mock_app = Mock()
    mock_app.get.return_value = [mock_face]
    
    with patch.object(EmbeddingService, '_get_face_analysis', return_value=mock_app):
        result = EmbeddingService.extract_face_encoding(mock_image)
    
    assert result is not None
    assert isinstance(result, np.ndarray)
    assert len(result) == 512
    assert result.dtype == np.float64


def test_compare_embeddings_identical():
    """
    ID: EMB-002
    Nombre: Comparar embeddings idénticos
    """
    embedding = np.random.rand(512).astype(np.float64)
    # Normalizar para que sea válido
    embedding = embedding / np.linalg.norm(embedding)
    
    match, similarity = EmbeddingService.compare_embeddings(
        embedding,
        embedding,
        tolerance=0.5
    )
    
    assert match is True
    assert similarity >= 0.5  # Debería ser muy similar (casi 1.0)


def test_compare_embeddings_similar():
    """
    ID: EMB-003
    Nombre: Comparar embeddings similares
    """
    embedding1 = np.random.rand(512).astype(np.float64)
    embedding1 = embedding1 / np.linalg.norm(embedding1)
    
    # Crear embedding similar (agregar pequeña variación)
    embedding2 = embedding1 + np.random.rand(512).astype(np.float64) * 0.1
    embedding2 = embedding2 / np.linalg.norm(embedding2)
    
    match, similarity = EmbeddingService.compare_embeddings(
        embedding1,
        embedding2,
        tolerance=0.5
    )
    
    assert isinstance(match, bool)
    assert isinstance(similarity, float)
    assert -1.0 <= similarity <= 1.0


def test_validate_embedding_valid():
    """
    ID: EMB-004
    Nombre: Validar embedding con dimensiones correctas
    """
    embedding = np.random.rand(settings.EMBEDDING_DIMENSIONS).astype(np.float64)
    
    result = EmbeddingService.validate_embedding(embedding)
    
    assert isinstance(result, np.ndarray)
    assert len(result) == settings.EMBEDDING_DIMENSIONS


def test_parse_embedding_from_list():
    """
    ID: EMB-005
    Nombre: Parsear embedding desde lista
    """
    embedding_list = [0.1] * 512
    
    result = EmbeddingService.parse_embedding(embedding_list)
    
    assert isinstance(result, list)
    assert len(result) == 512
    assert result == embedding_list


def test_parse_embedding_from_numpy():
    """
    ID: EMB-006
    Nombre: Parsear embedding desde numpy array
    """
    embedding_array = np.random.rand(512).astype(np.float64)
    
    result = EmbeddingService.parse_embedding(embedding_array)
    
    assert isinstance(result, list)
    assert len(result) == 512


def test_calculate_cosine_similarity():
    """
    ID: EMB-007
    Nombre: Calcular similitud coseno entre embeddings
    """
    embedding1 = np.random.rand(512).astype(np.float64)
    embedding2 = np.random.rand(512).astype(np.float64)
    
    similarity = EmbeddingService.calculate_cosine_similarity(
        embedding1.tolist(),
        embedding2.tolist()
    )
    
    assert isinstance(similarity, float)
    assert -1.0 <= similarity <= 1.0


# ============================================================================
# ❌ CASOS DE ERROR
# ============================================================================

def test_extract_face_encoding_no_face():
    """
    ID: EMB-008
    Nombre: Error al extraer embedding sin rostro detectado
    """
    mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    mock_app = Mock()
    mock_app.get.return_value = []  # No se detectó ningún rostro
    
    with patch.object(EmbeddingService, '_get_face_analysis', return_value=mock_app):
        with pytest.raises(ValueError) as exc_info:
            EmbeddingService.extract_face_encoding(mock_image)
        
        assert "no face" in str(exc_info.value).lower() or "detected" in str(exc_info.value).lower()


def test_extract_face_encoding_multiple_faces():
    """
    ID: EMB-009 (Extra)
    Nombre: Verificar que se selecciona el rostro más grande cuando hay múltiples rostros
    """
    mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    # Crear dos rostros con diferentes tamaños de bbox
    # rostro1: más pequeño (bbox: [10, 10, 50, 50] -> área = 40*40 = 1600)
    mock_face1 = Mock()
    mock_face1.normed_embedding = np.random.rand(512).astype(np.float64)
    mock_face1.bbox = np.array([10, 10, 50, 50], dtype=np.float32)
    
    # rostro2: más grande (bbox: [20, 20, 90, 90] -> área = 70*70 = 4900)
    mock_face2 = Mock()
    mock_face2.normed_embedding = np.random.rand(512).astype(np.float64)
    mock_face2.bbox = np.array([20, 20, 90, 90], dtype=np.float32)
    
    mock_app = Mock()
    mock_app.get.return_value = [mock_face1, mock_face2]  # Múltiples rostros
    
    with patch.object(EmbeddingService, '_get_face_analysis', return_value=mock_app):
        # Ahora el código selecciona el rostro más grande en lugar de lanzar error
        result = EmbeddingService.extract_face_encoding(mock_image)
        
        # Verificar que se devolvió un embedding válido
        assert result is not None
        assert isinstance(result, np.ndarray)
        assert len(result) == 512
        assert result.dtype == np.float64
        # Verificar que se usó el embedding del rostro más grande (mock_face2)
        np.testing.assert_array_equal(result, mock_face2.normed_embedding)


def test_validate_embedding_wrong_dimensions():
    """
    ID: EMB-008
    Nombre: Error al validar embedding con dimensiones incorrectas
    """
    embedding = np.random.rand(128).astype(np.float64)  # Dimensiones incorrectas (espera 512)
    
    with pytest.raises(ValueError) as exc_info:
        EmbeddingService.validate_embedding(embedding)
    
    assert "dimension" in str(exc_info.value).lower()

