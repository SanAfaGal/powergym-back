"""
Core face recognition service combining all operations.

This module provides a high-level API for face registration, authentication,
and comparison operations, orchestrating image processing, embedding extraction,
and database operations.
"""

import logging
from typing import Optional, Tuple, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from .image_processor import ImageProcessor
from .embedding import EmbeddingService
from .database import FaceDatabase

logger = logging.getLogger(__name__)


class FaceRecognitionService:
    """
    Main service for face recognition operations.
    
    This class provides high-level methods for face recognition workflows,
    including registration, authentication, comparison, and management operations.
    """

    @staticmethod
    def extract_face_encoding(image_base64: str) -> Tuple[List[float], bytes]:
        """
        Extract face encoding and create thumbnail from base64 image.

        Args:
            image_base64: Base64 encoded image string (with or without data URI prefix)

        Returns:
            Tuple of (embedding vector as list of floats, thumbnail as bytes)

        Raises:
            ValueError: If image processing or face extraction fails
        """
        try:
            logger.debug("Extracting face encoding from image")
            image_array = ImageProcessor.decode_base64_image(image_base64)

            face_encoding = EmbeddingService.extract_face_encoding(image_array)
            embedding = face_encoding.tolist()

            thumbnail = ImageProcessor.create_thumbnail(image_array)
            
            logger.debug(f"Successfully extracted face encoding (dimensions: {len(embedding)})")
            return embedding, thumbnail
            
        except ValueError as ve:
            logger.error(f"Face encoding extraction failed: {ve}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error extracting face encoding: {e}", exc_info=True)
            raise ValueError(f"Failed to extract face encoding: {str(e)}") from e

    @staticmethod
    def compare_faces(
            embedding_1: Any,
            embedding_2: Any,
            tolerance: Optional[float] = None
    ) -> Tuple[bool, float]:
        """
        Compare two face embeddings for similarity.

        Args:
            embedding_1: First face embedding (list, numpy array, or compatible format)
            embedding_2: Second face embedding (list, numpy array, or compatible format)
            tolerance: Optional similarity threshold (uses config default if None)

        Returns:
            Tuple of (is_match: bool, similarity_score: float)
            - is_match: True if similarity >= tolerance
            - similarity_score: Cosine similarity score (0.0-1.0)

        Raises:
            ValueError: If embeddings cannot be parsed or compared
        """
        try:
            logger.debug("Comparing two face embeddings")
            match, similarity = EmbeddingService.compare_embeddings(
                embedding_1,
                embedding_2,
                tolerance
            )
            logger.debug(f"Face comparison result: match={match}, similarity={similarity:.4f}")
            return match, similarity
        except ValueError as ve:
            logger.error(f"Face comparison failed: {ve}")
            raise

    @staticmethod
    def register_face(db: Session, client_id: UUID, image_base64: str) -> Dict[str, Any]:
        """
        Register a face biometric for a client.

        Args:
            db: Database session
            client_id: UUID of the client
            image_base64: Base64 encoded face image

        Returns:
            Dictionary with success status, biometric_id, and client_id.
            On failure, returns dict with success=False and error message.
        """
        try:
            logger.info(f"Registering face biometric for client {client_id}")
            embedding, thumbnail = FaceRecognitionService.extract_face_encoding(image_base64)

            result = FaceDatabase.store_face_biometric(
                db=db,
                client_id=client_id,
                embedding=embedding,
                thumbnail=thumbnail
            )

            if result.get("success"):
                logger.info(f"Successfully registered face biometric for client {client_id}")
            else:
                logger.warning(f"Failed to register face biometric for client {client_id}: {result.get('error')}")

            return result

        except ValueError as ve:
            logger.error(f"Face registration validation error for client {client_id}: {ve}")
            return {
                "success": False,
                "error": str(ve)
            }
        except Exception as e:
            logger.error(f"Unexpected error registering face for client {client_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Registration failed: {str(e)}"
            }

    @staticmethod
    def authenticate_face(
            db: Session,
            image_base64: str,
            tolerance: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Authenticate a client by face image using vector similarity search.

        Args:
            db: Database session
            image_base64: Base64 encoded face image
            tolerance: Optional similarity threshold (uses config default if None)

        Returns:
            Dictionary with authentication result containing:
            - success: Boolean indicating authentication success
            - client_id: UUID of matched client (if successful)
            - client_info: Client information dictionary (if successful)
            - confidence: Similarity score (if successful)
            - distance: Distance score (if successful)
            - error: Error message (if failed)
        """
        try:
            logger.info("Authenticating face")
            embedding, _ = FaceRecognitionService.extract_face_encoding(image_base64)

            if tolerance is None:
                from app.core.config import settings
                tolerance = settings.FACE_RECOGNITION_TOLERANCE

            logger.debug(f"Searching for similar faces with tolerance {tolerance}")
            similar_faces = FaceDatabase.search_similar_faces(
                db=db,
                embedding=embedding,
                limit=5,
                distance_threshold=tolerance
            )

            if not similar_faces:
                logger.warning("No matching face found during authentication")
                return {
                    "success": False,
                    "error": "No matching face found"
                }

            best_match = similar_faces[0]
            logger.debug(f"Best match found: client_id={best_match['client_id']}, similarity={best_match['similarity']:.4f}")
            
            client_info = FaceDatabase.get_client_info(db, best_match["client_id"])

            if client_info:
                logger.info(f"Successfully authenticated face for client {best_match['client_id']}")
                return {
                    "success": True,
                    "client_id": best_match["client_id"],
                    "client_info": client_info,
                    "confidence": best_match["similarity"],
                    "distance": best_match["distance"]
                }

            logger.warning(f"Client {best_match['client_id']} not found or inactive")
            return {
                "success": False,
                "error": "No matching face found"
            }

        except ValueError as ve:
            logger.error(f"Face authentication validation error: {ve}")
            return {
                "success": False,
                "error": str(ve)
            }
        except Exception as e:
            logger.error(f"Unexpected error during face authentication: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Authentication failed: {str(e)}"
            }

    @staticmethod
    def update_face(db: Session, client_id: UUID, image_base64: str) -> Dict[str, Any]:
        """
        Update face biometric for a client.

        This method deactivates existing face biometrics and registers a new one,
        effectively updating the client's face biometric data.

        Args:
            db: Database session
            client_id: UUID of the client
            image_base64: Base64 encoded face image

        Returns:
            Dictionary with success status and biometric info
        """
        logger.info(f"Updating face biometric for client {client_id}")
        return FaceRecognitionService.register_face(db, client_id, image_base64)

    @staticmethod
    def delete_face(db: Session, client_id: UUID) -> Dict[str, Any]:
        """
        Delete (deactivate) face biometric for a client.

        Args:
            db: Database session
            client_id: UUID of the client

        Returns:
            Dictionary with success status and message or error
        """
        try:
            logger.info(f"Deleting face biometric for client {client_id}")
            result = FaceDatabase.deactivate_face_biometric(db, client_id)
            
            if result.get("success"):
                logger.info(f"Successfully deleted face biometric for client {client_id}")
            else:
                logger.warning(f"Failed to delete face biometric for client {client_id}: {result.get('error')}")
            
            return result
        except Exception as e:
            logger.error(f"Unexpected error deleting face biometric for client {client_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Deletion failed: {str(e)}"
            }

    @staticmethod
    def compare_two_faces(
            image_base64_1: str,
            image_base64_2: str,
            tolerance: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Compare two face images directly without database lookup.

        Args:
            image_base64_1: First base64 encoded face image
            image_base64_2: Second base64 encoded face image
            tolerance: Optional similarity threshold (uses config default if None)

        Returns:
            Dictionary with comparison result containing:
            - success: Boolean indicating operation success
            - match: Boolean indicating if faces match
            - distance: Distance score (lower is more similar)
            - confidence: Confidence score (0.0-1.0, higher is more similar)
            - error: Error message (if failed)
        """
        try:
            logger.debug("Comparing two face images")
            embedding_1, _ = FaceRecognitionService.extract_face_encoding(image_base64_1)
            embedding_2, _ = FaceRecognitionService.extract_face_encoding(image_base64_2)

            match, similarity = FaceRecognitionService.compare_faces(
                embedding_1,
                embedding_2,
                tolerance
            )

            # Convert similarity to distance and confidence
            distance = 1.0 - similarity
            confidence = max(0.0, similarity)

            logger.debug(f"Face comparison result: match={match}, similarity={similarity:.4f}, confidence={confidence:.4f}")

            return {
                "success": True,
                "match": match,
                "distance": distance,
                "confidence": confidence
            }

        except ValueError as ve:
            logger.error(f"Face comparison validation error: {ve}")
            return {
                "success": False,
                "error": str(ve)
            }
        except Exception as e:
            logger.error(f"Unexpected error comparing faces: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Comparison failed: {str(e)}"
            }
