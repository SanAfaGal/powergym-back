"""
Database operations for face recognition biometric data.

This module handles CRUD operations for face biometrics with encryption,
including storing, retrieving, searching, and deactivating face biometric records.
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.biometric_repository import BiometricRepository
from app.repositories.client_repository import ClientRepository
from app.db.models import BiometricTypeEnum
from app.core.encryption import get_encryption_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class FaceDatabase:
    """
    Handles database operations for face biometric data.
    
    This class provides methods for storing, retrieving, searching, and managing
    face biometric records with proper encryption and error handling.
    """

    @staticmethod
    def store_face_biometric(
        db: Session,
        client_id: UUID,
        embedding: List[float],
        thumbnail: bytes
    ) -> Dict[str, Any]:
        """
        Store face biometric data in database with native vector storage.
        
        Only thumbnail is encrypted for privacy. Existing face biometrics for
        the client are automatically deactivated before storing the new one.

        Args:
            db: Database session
            client_id: UUID of the client
            embedding: Face embedding vector (typically 512-dimensional for InsightFace)
            thumbnail: Thumbnail image bytes

        Returns:
            Dictionary with success status, biometric_id, and client_id.
            On failure, returns dict with success=False and error message.

        Raises:
            ValueError: If embedding dimensions don't match expected size
        """
        try:
            logger.info(f"Storing face biometric for client {client_id}")
            
            # Validate embedding dimensions
            if len(embedding) != settings.EMBEDDING_DIMENSIONS:
                error_msg = (
                    f"Invalid embedding dimensions: expected {settings.EMBEDDING_DIMENSIONS}, "
                    f"got {len(embedding)}"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Deactivate existing face biometrics for this client
            existing_biometrics = BiometricRepository.get_by_client_id(
                db, client_id, is_active=True
            )

            deactivated_count = 0
            for biometric in existing_biometrics:
                if biometric.type == BiometricTypeEnum.FACE:
                    BiometricRepository.update(db, biometric.id, is_active=False)
                    deactivated_count += 1
            
            if deactivated_count > 0:
                logger.debug(f"Deactivated {deactivated_count} existing face biometric(s) for client {client_id}")

            # Encrypt thumbnail
            encryption_service = get_encryption_service()
            encrypted_thumbnail = encryption_service.encrypt_image_data(thumbnail)

            # Prepare metadata
            meta_info = {
                "encoding_version": "insightface_v1_vector",
                "model": settings.INSIGHTFACE_MODEL,
                "embedding_dimensions": settings.EMBEDDING_DIMENSIONS,
                "encryption": "AES-256-GCM",
                "thumbnail_quality": settings.THUMBNAIL_COMPRESSION_QUALITY
            }

            # Create new biometric record
            biometric = BiometricRepository.create(
                db=db,
                client_id=client_id,
                biometric_type=BiometricTypeEnum.FACE,
                thumbnail=encrypted_thumbnail,
                embedding_vector=embedding,
                meta_info=meta_info
            )

            logger.info(f"Successfully stored face biometric {biometric.id} for client {client_id}")
            
            return {
                "success": True,
                "biometric_id": str(biometric.id),
                "client_id": str(client_id)
            }

        except ValueError as ve:
            logger.error(f"Validation error storing face biometric: {ve}")
            return {
                "success": False,
                "error": str(ve)
            }
        except SQLAlchemyError as e:
            logger.error(f"Database error storing face biometric for client {client_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": "Database operation failed. Please try again later."
            }
        except Exception as e:
            logger.error(f"Unexpected error storing face biometric for client {client_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to store face biometric: {str(e)}"
            }

    @staticmethod
    def get_all_active_face_biometrics(db: Session) -> List[Dict[str, Any]]:
        """
        Retrieve all active face biometric records from database.

        Args:
            db: Database session

        Returns:
            List of dictionaries containing biometric records with vector embeddings

        Raises:
            SQLAlchemyError: If database query fails
        """
        try:
            logger.debug("Retrieving all active face biometrics")
            biometrics = BiometricRepository.get_by_type(
                db, BiometricTypeEnum.FACE, is_active=True
            )

            result = [
                {
                    "id": str(bio.id),
                    "client_id": str(bio.client_id),
                    "embedding_vector": bio.embedding_vector,
                    "meta_info": bio.meta_info
                }
                for bio in biometrics
            ]
            
            logger.debug(f"Retrieved {len(result)} active face biometric records")
            return result

        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving face biometrics: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving face biometrics: {e}", exc_info=True)
            raise RuntimeError(f"Failed to retrieve biometric data: {str(e)}") from e

    @staticmethod
    def search_similar_faces(
        db: Session,
        embedding: List[float],
        limit: int = 10,
        distance_threshold: float = 0.6,
        exclude_client_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar faces using native vector similarity search.

        Args:
            db: Database session
            embedding: Face embedding vector to search for
            limit: Maximum number of results to return
            distance_threshold: Maximum cosine distance for matches (0.0-1.0)
            exclude_client_id: Optional client ID to exclude from results

        Returns:
            List of matching biometric records with similarity scores, sorted by distance

        Raises:
            ValueError: If embedding dimensions don't match expected size
            SQLAlchemyError: If database search operation fails
        """
        try:
            # Validate embedding dimensions
            if len(embedding) != settings.EMBEDDING_DIMENSIONS:
                error_msg = (
                    f"Invalid embedding dimensions: expected {settings.EMBEDDING_DIMENSIONS}, "
                    f"got {len(embedding)}"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.debug(f"Searching for similar faces with threshold {distance_threshold}, limit {limit}, exclude_client_id={exclude_client_id}")
            
            results = BiometricRepository.search_similar_embeddings(
                db=db,
                embedding_vector=embedding,
                biometric_type=BiometricTypeEnum.FACE,
                limit=limit,
                distance_threshold=distance_threshold,
                exclude_client_id=exclude_client_id
            )

            matches = [
                {
                    "id": str(bio.id),
                    "client_id": str(bio.client_id),
                    "embedding_vector": bio.embedding_vector,
                    "distance": distance,
                    "similarity": 1.0 - distance,
                    "meta_info": bio.meta_info
                }
                for bio, distance in results
            ]
            
            logger.debug(f"Found {len(matches)} similar face matches")
            return matches

        except ValueError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error searching similar faces: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error searching similar faces: {e}", exc_info=True)
            raise RuntimeError(f"Failed to search similar faces: {str(e)}") from e

    @staticmethod
    def get_client_info(db: Session, client_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve client information by ID.

        Args:
            db: Database session
            client_id: UUID string of the client

        Returns:
            Client information dictionary or None if not found or inactive

        Raises:
            ValueError: If client_id is not a valid UUID
            SQLAlchemyError: If database query fails
        """
        try:
            from uuid import UUID as UUID_Parser
            
            try:
                client_uuid = UUID_Parser(client_id)
            except ValueError as ve:
                logger.error(f"Invalid UUID format for client_id: {client_id}")
                raise ValueError(f"Invalid client ID format: {client_id}") from ve

            logger.debug(f"Retrieving client info for {client_id}")
            client = ClientRepository.get_by_id(db, client_uuid)

            if client and client.is_active:
                client_info = {
                    "id": str(client.id),
                    "dni_type": client.dni_type.value,
                    "dni_number": client.dni_number,
                    "first_name": client.first_name,
                    "middle_name": client.middle_name,
                    "last_name": client.last_name,
                    "second_last_name": client.second_last_name,
                    "phone": client.phone,
                    "alternative_phone": client.alternative_phone,
                    "birth_date": client.birth_date.isoformat(),
                    "gender": client.gender.value,
                    "address": client.address,
                    "is_active": client.is_active,
                    "created_at": client.created_at.isoformat(),
                    "updated_at": client.updated_at.isoformat(),
                    "meta_info": client.meta_info
                }
                logger.debug(f"Retrieved client info for {client_id}")
                return client_info

            logger.debug(f"Client {client_id} not found or inactive")
            return None

        except ValueError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving client info for {client_id}: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving client info for {client_id}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to retrieve client info: {str(e)}") from e

    @staticmethod
    def deactivate_face_biometric(db: Session, client_id: UUID) -> Dict[str, Any]:
        """
        Deactivate all face biometric records for a client.

        Args:
            db: Database session
            client_id: UUID of the client

        Returns:
            Dictionary with success status and message or error

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            logger.info(f"Deactivating face biometrics for client {client_id}")
            
            biometrics = BiometricRepository.get_by_client_id(
                db, client_id, is_active=True
            )

            deactivated_count = 0
            for biometric in biometrics:
                if biometric.type == BiometricTypeEnum.FACE:
                    BiometricRepository.update(db, biometric.id, is_active=False)
                    deactivated_count += 1

            if deactivated_count > 0:
                logger.info(f"Successfully deactivated {deactivated_count} face biometric(s) for client {client_id}")
                return {
                    "success": True,
                    "message": "Face biometric deactivated successfully"
                }

            logger.warning(f"No active face biometric found for client {client_id}")
            return {
                "success": False,
                "error": "No active face biometric found"
            }

        except SQLAlchemyError as e:
            logger.error(f"Database error deactivating face biometric for client {client_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": "Database operation failed. Please try again later."
            }
        except Exception as e:
            logger.error(f"Unexpected error deactivating face biometric for client {client_id}: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Failed to deactivate face biometric: {str(e)}"
            }
