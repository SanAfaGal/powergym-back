"""
Embedding generation and comparison utilities for face recognition.

This module handles face encoding extraction and similarity calculations
using InsightFace, including face detection, embedding extraction, and
similarity metrics computation.
"""

import logging
from typing import List, Tuple, Optional, Any, Dict
import numpy as np
import numpy as np
try:
    import cv2
    from insightface.app import FaceAnalysis
except ImportError:
    # Allow application to start even if AI dependencies are missing
    # Functionality will be guarded by FACE_RECOGNITION_ENABLED
    cv2 = None
    FaceAnalysis = None

from app.core.config import settings
from app.core.constants import ERROR_FACE_QUALITY_TOO_LOW, ERROR_FACE_TOO_SMALL

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Handles face embedding generation and comparison operations using InsightFace.
    
    This class provides methods for extracting face embeddings from images,
    comparing embeddings for similarity, and validating embedding formats.
    """

    _app: Optional[FaceAnalysis] = None

    @classmethod
    def _get_face_analysis(cls) -> FaceAnalysis:
        """
        Lazy initialization of InsightFace FaceAnalysis.
        
        Returns:
            Initialized FaceAnalysis instance
            
        Raises:
            RuntimeError: If InsightFace model initialization fails or is disabled
        """
        if not settings.FACE_RECOGNITION_ENABLED:
            logger.warning("Attempted to initialize face recognition model while disabled")
            raise RuntimeError("Face recognition is disabled by configuration")

        if cls._app is None:
            try:
                logger.info(f"Initializing InsightFace model: {settings.INSIGHTFACE_MODEL}")
                
                # Determine execution provider based on configuration
                providers = ['CPUExecutionProvider']
                if settings.INSIGHTFACE_CTX_ID >= 0:
                    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
                    logger.debug(f"Using GPU context ID: {settings.INSIGHTFACE_CTX_ID}")
                else:
                    logger.debug("Using CPU execution provider")

                cls._app = FaceAnalysis(
                    name=settings.INSIGHTFACE_MODEL,
                    providers=providers
                )
                cls._app.prepare(
                    ctx_id=settings.INSIGHTFACE_CTX_ID,
                    det_size=(settings.INSIGHTFACE_DET_SIZE, settings.INSIGHTFACE_DET_SIZE)
                )
                logger.info("InsightFace model initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize InsightFace model: {e}", exc_info=True)
                raise RuntimeError(f"Failed to initialize InsightFace model: {str(e)}") from e
        return cls._app

    @staticmethod
    def extract_face_encoding(image_array: np.ndarray) -> np.ndarray:
        """
        Extract face encoding from an image array using InsightFace.

        Args:
            image_array: Image as numpy array in RGB format

        Returns:
            512-dimensional face encoding as numpy array

        Raises:
            ValueError: If no face, multiple faces, or encoding extraction fails
        """
        app = EmbeddingService._get_face_analysis()

        # InsightFace espera BGR, convertir si viene en RGB
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            # Verificar si ya está en BGR o necesita conversión
            # Asumimos que viene en RGB del frontend
            image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image_array

        # Detectar y extraer embeddings
        faces = app.get(image_bgr)

        if len(faces) == 0:
            logger.warning("No face detected in the image")
            raise ValueError("No face detected in the image")

        if len(faces) > 1:
            logger.warning(f"Multiple faces detected ({len(faces)}). Rejecting registration.")
            from app.core.constants import ERROR_MULTIPLE_FACES_DETECTED
            raise ValueError(ERROR_MULTIPLE_FACES_DETECTED)

        # Embedding is already L2-normalized by InsightFace
        embedding = faces[0].normed_embedding

        # Convert to float64 for consistency
        embedding_array = embedding.astype(np.float64)
        logger.debug(f"Extracted face embedding with dimensions: {len(embedding_array)}")
        return embedding_array

    @staticmethod
    def validate_embedding(embedding: Any) -> np.ndarray:
        """
        Validate and convert embedding to numpy array with correct dimensions.

        Args:
            embedding: Embedding (list, numpy array, or string)

        Returns:
            Embedding as numpy array with dimensions from settings.EMBEDDING_DIMENSIONS

        Raises:
            ValueError: If embedding format is invalid or dimension mismatch
        """
        if isinstance(embedding, list):
            parsed_embedding = embedding
        else:
            parsed_embedding = EmbeddingService.parse_embedding(embedding)

        try:
            embedding_array = np.array(parsed_embedding, dtype=np.float64)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Failed to convert embedding to numpy array: {str(e)}, "
                f"type: {type(parsed_embedding)}"
            )

        expected_dim = settings.EMBEDDING_DIMENSIONS
        if len(embedding_array) != expected_dim:
            raise ValueError(
                f"Expected {expected_dim}-dimensional embedding, got {len(embedding_array)} dimensions"
            )

        return embedding_array

    @staticmethod
    def parse_embedding(embedding: Any) -> List[float]:
        """
        Parse embedding from various formats to list of floats.

        Args:
            embedding: Embedding in various formats (list, numpy array, string, JSON)

        Returns:
            Embedding as list of floats

        Raises:
            ValueError: If parsing fails or format is unsupported
        """
        if embedding is None:
            raise ValueError("Embedding cannot be None")

        if isinstance(embedding, list):
            return embedding

        if isinstance(embedding, np.ndarray):
            return embedding.tolist()

        if isinstance(embedding, str):
            import json
            try:
                parsed = json.loads(embedding)
                if isinstance(parsed, list):
                    return parsed
                raise ValueError(f"Parsed embedding is not a list, got {type(parsed)}")
            except json.JSONDecodeError:
                embedding_clean = embedding.strip('[]').replace(' ', '')
                try:
                    return [float(x) for x in embedding_clean.split(',') if x]
                except Exception as parse_error:
                    raise ValueError(
                        f"Failed to parse embedding string: {str(parse_error)}"
                    )

        raise ValueError(f"Unsupported embedding type: {type(embedding)}")

    @staticmethod
    def compare_embeddings(
            embedding_1: Any,
            embedding_2: Any,
            tolerance: Optional[float] = None
    ) -> Tuple[bool, float]:
        """
        Compare two face embeddings for similarity using cosine similarity.

        InsightFace embeddings are L2-normalized, so we use cosine similarity
        (dot product) for comparison, which is more appropriate than Euclidean distance.

        Args:
            embedding_1: First embedding (typically 512-dimensional for InsightFace)
            embedding_2: Second embedding (typically 512-dimensional for InsightFace)
            tolerance: Similarity threshold (0.0-1.0, higher = more similar).
                      Default from config. Recommended: 0.4-0.6

        Returns:
            Tuple of (is_match: bool, similarity: float)
            - similarity: 1.0 = identical, 0.0 = orthogonal, -1.0 = opposite
            - is_match: True if similarity >= tolerance

        Raises:
            ValueError: If embeddings cannot be parsed or compared
        """
        if tolerance is None:
            tolerance = settings.FACE_RECOGNITION_TOLERANCE

        try:
            parsed_embedding_1 = (
                EmbeddingService.parse_embedding(embedding_1)
                if not isinstance(embedding_1, (list, np.ndarray))
                else embedding_1
            )
            parsed_embedding_2 = (
                EmbeddingService.parse_embedding(embedding_2)
                if not isinstance(embedding_2, (list, np.ndarray))
                else embedding_2
            )
        except ValueError as e:
            raise ValueError(f"Failed to parse embeddings for comparison: {str(e)}")

        face_encoding_1 = EmbeddingService.validate_embedding(parsed_embedding_1)
        face_encoding_2 = EmbeddingService.validate_embedding(parsed_embedding_2)

        # Calculate cosine similarity (dot product of L2-normalized vectors)
        # Since InsightFace already normalizes embeddings, dot product IS cosine similarity
        similarity = float(np.dot(face_encoding_1, face_encoding_2))

        # Higher similarity = match (opposite of Euclidean distance)
        match = similarity >= tolerance

        logger.debug(f"Embedding comparison: similarity={similarity:.4f}, tolerance={tolerance:.4f}, match={match}")
        return match, similarity

    @staticmethod
    def calculate_euclidean_distance(
            embedding_1: List[float],
            embedding_2: List[float]
    ) -> float:
        """
        Calculate Euclidean distance between two embeddings.

        Note: Para InsightFace, cosine similarity es más apropiado.
        Esta función se mantiene por compatibilidad.

        Args:
            embedding_1: First embedding (512-dimensional)
            embedding_2: Second embedding (512-dimensional)

        Returns:
            Euclidean distance (lower = more similar)
        """
        vec1 = np.array(embedding_1, dtype=np.float64)
        vec2 = np.array(embedding_2, dtype=np.float64)

        distance = np.linalg.norm(vec1 - vec2)

        return float(distance)

    @staticmethod
    def calculate_cosine_similarity(
            embedding_1: List[float],
            embedding_2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding_1: First embedding (512-dimensional)
            embedding_2: Second embedding (512-dimensional)

        Returns:
            Cosine similarity score (1.0 = identical, 0.0 = orthogonal, -1.0 = opposite)
        """
        vec1 = np.array(embedding_1, dtype=np.float64)
        vec2 = np.array(embedding_2, dtype=np.float64)

        # Normalizar vectores
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        # Calcular similitud coseno
        similarity = np.dot(vec1, vec2) / (norm1 * norm2)

        return float(similarity)

    @staticmethod
    def get_face_quality_score(image_array: np.ndarray) -> Dict[str, Any]:
        """
        Evaluate the quality of a facial image for recognition.

        This method analyzes various image quality metrics including face size,
        brightness, and sharpness to provide recommendations for better recognition.

        Args:
            image_array: Image as numpy array in RGB format

        Returns:
            Dictionary with quality metrics:
            - score: Overall quality score (0-1)
            - brightness: Brightness level
            - sharpness: Sharpness level (Laplacian variance)
            - face_size: Ratio of face area to image area
            - face_dimensions: Width and height of detected face
            - recommendations: List of quality improvement recommendations
        """
        app = EmbeddingService._get_face_analysis()

        # Convert to BGR
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image_array

        faces = app.get(image_bgr)

        if len(faces) == 0:
            logger.warning("No face detected for quality assessment")
            return {
                'score': 0.0,
                'brightness': None,
                'sharpness': None,
                'face_size': None,
                'face_dimensions': None,
                'recommendations': ['No face detected']
            }

        face = faces[0]
        recommendations = []

        # 1. Face size
        bbox = face.bbox.astype(int)
        face_width = bbox[2] - bbox[0]
        face_height = bbox[3] - bbox[1]
        face_area = face_width * face_height
        image_area = image_array.shape[0] * image_array.shape[1]
        face_ratio = face_area / image_area

        min_ratio = settings.FACE_VALIDATION_MIN_FACE_SIZE_RATIO
        if face_ratio < min_ratio:
            recommendations.append('Face is too small - move closer to camera')
        elif face_ratio > 0.8:
            recommendations.append('Face is too close - move back from camera')

        # 2. Brightness
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
        brightness = float(np.mean(gray))

        # Improved brightness validation with tighter range
        if brightness < 70:  # Stricter minimum
            recommendations.append('Image is too dark - improve lighting')
        elif brightness > 180:  # Stricter maximum
            recommendations.append('Image is too bright - reduce lighting')
        elif not (80 <= brightness <= 160):  # Warn if outside optimal range
            recommendations.append('Lighting could be improved for better recognition')

        # 3. Sharpness (Laplacian variance)
        sharpness = float(EmbeddingService._calculate_sharpness(gray))

        if sharpness < 150:  # Stricter minimum
            recommendations.append('Image is blurry - hold camera steady')
        elif sharpness < 300:  # Warn if below optimal
            recommendations.append('Image could be sharper for better recognition')

        # 4. Overall score (normalized 0-1)
        face_score = min(face_ratio * 10, 1.0)  # Optimal around 0.1-0.3
        brightness_score = 1.0 - abs(brightness - 120) / 120  # Optimal around 120
        sharpness_score = min(sharpness / 600, 1.0)  # Optimal > 600

        overall_score = (face_score + brightness_score + sharpness_score) / 3

        return {
            'score': float(overall_score),
            'brightness': brightness,
            'sharpness': sharpness,
            'face_size': float(face_ratio),
            'face_dimensions': {
                'width': int(face_width),
                'height': int(face_height)
            },
            'recommendations': recommendations if recommendations else ['Image quality is good']
        }

    @staticmethod
    def _calculate_sharpness(gray: np.ndarray) -> float:
        """
        Calculate image sharpness using Laplacian variance.
        
        Args:
            gray: Grayscale image array
            
        Returns:
            Sharpness score (higher = sharper)
        """
        try:
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            return float(laplacian.var())
        except Exception as e:
            logger.debug(f"Error calculating sharpness: {e}")
            return 0.0

    @staticmethod
    def validate_face_quality(image_array: np.ndarray) -> Tuple[bool, Optional[str]]:
        """
        Validate face quality meets minimum requirements.
        
        Args:
            image_array: Image as numpy array in RGB format
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        try:
            quality_data = EmbeddingService.get_face_quality_score(image_array)
            
            min_quality = settings.FACE_VALIDATION_MIN_QUALITY_SCORE
            quality_score = quality_data['score']
            
            if quality_score < min_quality:
                logger.warning(
                    f"Face quality too low: score={quality_score:.3f} "
                    f"(min: {min_quality:.3f})"
                )
                return False, ERROR_FACE_QUALITY_TOO_LOW
            
            # Also validate face size
            face_ratio = quality_data.get('face_size', 0.0)
            min_ratio = settings.FACE_VALIDATION_MIN_FACE_SIZE_RATIO
            
            if face_ratio < min_ratio:
                logger.warning(
                    f"Face too small: ratio={face_ratio:.4f} (min: {min_ratio:.4f})"
                )
                return False, ERROR_FACE_TOO_SMALL
            
            logger.debug(
                f"Face quality validation passed: score={quality_score:.3f}, "
                f"ratio={face_ratio:.4f}"
            )
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating face quality: {e}", exc_info=True)
            return False, ERROR_FACE_QUALITY_TOO_LOW

    @staticmethod
    def extract_multiple_faces(image_array: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect and extract embeddings from multiple faces in an image.

        Useful for group photos or bulk registration scenarios.

        Args:
            image_array: Image as numpy array in RGB format

        Returns:
            List of dictionaries with information for each detected face:
            - embedding: Face embedding vector (typically 512-dim)
            - bbox: Bounding box coordinates [x1, y1, x2, y2]
            - confidence: Detection confidence score
            - landmarks: Facial landmarks (if available)
            - age: Estimated age (if available)
            - gender: Estimated gender (if available)
        """
        app = EmbeddingService._get_face_analysis()

        # Convertir a BGR
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image_array

        faces = app.get(image_bgr)

        results = []
        for face in faces:
            results.append({
                'embedding': face.normed_embedding.astype(np.float64).tolist(),
                'bbox': face.bbox.astype(int).tolist(),
                'confidence': float(face.det_score),
                'landmarks': face.kps.astype(int).tolist() if hasattr(face, 'kps') else None,
                'age': int(face.age) if hasattr(face, 'age') else None,
                'gender': 'M' if face.gender == 1 else 'F' if hasattr(face, 'gender') else None
            })

        logger.debug(f"Extracted {len(results)} face(s) from image")
        return results

    @staticmethod
    def find_best_match(
            query_embedding: Any,
            candidate_embeddings: List[Any],
            tolerance: Optional[float] = None
    ) -> Tuple[Optional[int], float]:
        """
        Find the best match between a query embedding and a list of candidate embeddings.

        Args:
            query_embedding: Embedding to search for
            candidate_embeddings: List of candidate embeddings to compare against
            tolerance: Minimum similarity threshold (uses config default if None)

        Returns:
            Tuple of (best_match_index: Optional[int], best_similarity: float)
            - best_match_index: Index of the best match, or None if none exceeds threshold
            - best_similarity: Similarity score of the best match
        """
        if tolerance is None:
            tolerance = settings.FACE_RECOGNITION_TOLERANCE

        query_emb = EmbeddingService.validate_embedding(query_embedding)

        best_similarity = -1.0
        best_index = None

        for idx, candidate in enumerate(candidate_embeddings):
            candidate_emb = EmbeddingService.validate_embedding(candidate)
            similarity = float(np.dot(query_emb, candidate_emb))

            if similarity > best_similarity:
                best_similarity = similarity
                best_index = idx

        # Only return match if it exceeds the threshold
        if best_similarity < tolerance:
            logger.debug(f"Best match similarity {best_similarity:.4f} below threshold {tolerance:.4f}")
            return None, best_similarity

        logger.debug(f"Best match found at index {best_index} with similarity {best_similarity:.4f}")
        return best_index, best_similarity
