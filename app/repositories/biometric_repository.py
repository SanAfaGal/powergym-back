from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.models import ClientBiometricModel, BiometricTypeEnum
from typing import Optional, List, Tuple
from uuid import UUID

class BiometricRepository:
    @staticmethod
    def create(db: Session, client_id: UUID, biometric_type: BiometricTypeEnum,
               thumbnail: Optional[str] = None,
               embedding_vector: Optional[List[float]] = None, meta_info: dict = None) -> ClientBiometricModel:
        """
        Create a new biometric record in the database.
        """
        db_biometric = ClientBiometricModel(
            client_id=client_id,
            type=biometric_type,
            thumbnail=thumbnail,
            embedding_vector=embedding_vector,
            is_active=True,
            meta_info=meta_info or {}
        )
        db.add(db_biometric)
        db.commit()
        db.refresh(db_biometric)
        return db_biometric

    @staticmethod
    def get_by_id(db: Session, biometric_id: UUID) -> Optional[ClientBiometricModel]:
        """
        Get biometric by ID.
        """
        return db.query(ClientBiometricModel).filter(ClientBiometricModel.id == biometric_id).first()

    @staticmethod
    def get_by_client_id(db: Session, client_id: UUID,
                        is_active: Optional[bool] = None) -> List[ClientBiometricModel]:
        """
        Get all biometric records for a specific client.
        """
        query = db.query(ClientBiometricModel).filter(ClientBiometricModel.client_id == client_id)

        if is_active is not None:
            query = query.filter(ClientBiometricModel.is_active == is_active)

        return query.all()

    @staticmethod
    def get_by_type(db: Session, biometric_type: BiometricTypeEnum,
                   is_active: bool = True) -> List[ClientBiometricModel]:
        """
        Get all biometric records of a specific type.
        """
        return db.query(ClientBiometricModel).filter(
            ClientBiometricModel.type == biometric_type,
            ClientBiometricModel.is_active == is_active
        ).all()

    @staticmethod
    def get_all(db: Session, is_active: Optional[bool] = None,
                limit: int = 1000, offset: int = 0) -> List[ClientBiometricModel]:
        """
        Get all biometric records with optional filtering.
        """
        query = db.query(ClientBiometricModel)

        if is_active is not None:
            query = query.filter(ClientBiometricModel.is_active == is_active)

        query = query.order_by(ClientBiometricModel.created_at.desc()).offset(offset).limit(limit)
        return query.all()

    @staticmethod
    def update(db: Session, biometric_id: UUID, **kwargs) -> Optional[ClientBiometricModel]:
        """
        Update biometric by ID.
        """
        biometric = db.query(ClientBiometricModel).filter(
            ClientBiometricModel.id == biometric_id
        ).first()
        if not biometric:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(biometric, key):
                setattr(biometric, key, value)

        db.commit()
        db.refresh(biometric)
        return biometric

    @staticmethod
    def delete(db: Session, biometric_id: UUID) -> bool:
        """
        Soft delete biometric by setting is_active to False.
        """
        biometric = db.query(ClientBiometricModel).filter(
            ClientBiometricModel.id == biometric_id
        ).first()
        if not biometric:
            return False

        biometric.is_active = False
        db.commit()
        return True

    @staticmethod
    def search_similar_embeddings(
        db: Session,
        embedding_vector: List[float],
        biometric_type: BiometricTypeEnum,
        limit: int = 10,
        distance_threshold: float = 0.6
    ) -> List[Tuple[ClientBiometricModel, float]]:
        """
        Search for similar embeddings using vector similarity.
        Uses cosine distance operator (<=>).

        Args:
            db: Database session
            embedding_vector: 128-dimensional embedding to search for
            biometric_type: Type of biometric to search
            limit: Maximum number of results
            distance_threshold: Maximum distance for matches (lower = more similar)

        Returns:
            List of tuples (biometric, distance) ordered by similarity
        """
        query = text("""
            SELECT *, embedding_vector <=> :embedding_vector as distance
            FROM client_biometrics
            WHERE type = :biometric_type
              AND is_active = true
              AND embedding_vector IS NOT NULL
              AND embedding_vector <=> :embedding_vector <= :distance_threshold
            ORDER BY distance
            LIMIT :limit
        """)

        result = db.execute(
            query,
            {
                "embedding_vector": str(embedding_vector),
                "biometric_type": biometric_type.value,
                "distance_threshold": distance_threshold,
                "limit": limit
            }
        )

        results = []
        for row in result.mappings():
            biometric = db.query(ClientBiometricModel).filter(
                ClientBiometricModel.id == row["id"]
            ).first()
            if biometric:
                results.append((biometric, float(row["distance"])))

        return results
