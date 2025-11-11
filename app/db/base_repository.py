"""
Base repository class for PowerGym API.

This module provides a base repository class with common CRUD operations
that can be extended by specific repositories to reduce code duplication.
"""

from typing import Generic, TypeVar, Optional, Sequence, Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.base import Base

# Type variable for the model type
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository class providing common CRUD operations.

    This class implements the Repository pattern, providing a clean interface
    for database operations. Specific repositories should inherit from this
    class and specify the model type.

    Example:
        class ClientRepository(BaseRepository[ClientModel]):
            def __init__(self, db: Session):
                super().__init__(db, ClientModel)
    """

    def __init__(self, db: Session, model: Type[ModelType]) -> None:
        """
        Initialize the repository.

        Args:
            db: SQLAlchemy database session
            model: SQLAlchemy model class
        """
        self.db = db
        self.model = model

    def get_by_id(self, entity_id: UUID) -> Optional[ModelType]:
        """
        Retrieve an entity by its ID.

        Args:
            entity_id: UUID of the entity

        Returns:
            Model instance if found, None otherwise
        """
        stmt = select(self.model).where(self.model.id == entity_id)
        return self.db.execute(stmt).scalars().first()

    def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[str] = None,
    ) -> Sequence[ModelType]:
        """
        Retrieve all entities with pagination.

        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            order_by: Optional column name to order by (default: created_at desc)

        Returns:
            List of model instances
        """
        stmt = select(self.model)

        if order_by:
            # Simple ordering by attribute name
            if hasattr(self.model, order_by):
                order_attr = getattr(self.model, order_by)
                stmt = stmt.order_by(order_attr.desc())
        else:
            # Default ordering by created_at if available
            if hasattr(self.model, "created_at"):
                stmt = stmt.order_by(self.model.created_at.desc())

        stmt = stmt.offset(offset).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def create(self, **kwargs) -> ModelType:
        """
        Create a new entity.

        Args:
            **kwargs: Attributes for the new entity

        Returns:
            Created model instance

        Raises:
            SQLAlchemyError: If database operation fails
        """
        entity = self.model(**kwargs)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity_id: UUID, **kwargs) -> Optional[ModelType]:
        """
        Update an entity by ID.

        Only non-None values are updated. Only existing attributes are modified.

        Args:
            entity_id: UUID of the entity to update
            **kwargs: Key-value pairs of attributes to update

        Returns:
            Updated model instance if found, None otherwise

        Raises:
            SQLAlchemyError: If database operation fails
        """
        entity = self.get_by_id(entity_id)
        if not entity:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(entity, key):
                setattr(entity, key, value)

        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, entity_id: UUID) -> bool:
        """
        Delete an entity by ID (hard delete).

        For soft deletes, override this method in the specific repository.

        Args:
            entity_id: UUID of the entity to delete

        Returns:
            True if deletion was successful, False if entity not found

        Raises:
            SQLAlchemyError: If database operation fails
        """
        entity = self.get_by_id(entity_id)
        if not entity:
            return False

        self.db.delete(entity)
        self.db.commit()
        return True

    def count(self) -> int:
        """
        Count total number of entities.

        Returns:
            Total count of entities
        """
        stmt = select(self.model)
        return len(self.db.execute(stmt).scalars().all())

    def exists(self, entity_id: UUID) -> bool:
        """
        Check if an entity exists by ID.

        Args:
            entity_id: UUID of the entity

        Returns:
            True if entity exists, False otherwise
        """
        return self.get_by_id(entity_id) is not None

