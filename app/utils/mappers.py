"""
Model to Schema mappers for PowerGym API.

This module provides reusable mapper functions to convert SQLAlchemy models
to Pydantic schemas, eliminating code duplication and ensuring consistency.
"""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from app.db.models import (
    ClientModel,
    DocumentTypeEnum,
    GenderTypeEnum,
)
from app.schemas.client import (
    Client,
    DocumentType,
    GenderType,
)

# Import UserModel for runtime use (not just type checking)
from app.db.models import UserModel

if TYPE_CHECKING:
    from app.schemas.user import User, UserInDB


def model_to_client_schema(model: ClientModel) -> Client:
    """
    Convert ClientModel to Client schema.

    This is the single source of truth for Client model-to-schema conversion.
    All service methods should use this function to ensure consistency.

    Args:
        model: ClientModel instance from database

    Returns:
        Client schema instance

    Raises:
        ValueError: If model is None or invalid
    """
    if model is None:
        raise ValueError("ClientModel cannot be None")

    return Client(
        id=model.id,
        dni_type=DocumentType(model.dni_type.value),
        dni_number=model.dni_number,
        first_name=model.first_name,
        middle_name=model.middle_name,
        last_name=model.last_name,
        second_last_name=model.second_last_name,
        phone=model.phone,
        alternative_phone=model.alternative_phone,
        birth_date=model.birth_date,
        gender=GenderType(model.gender.value),
        address=model.address,
        is_active=model.is_active,
        created_at=model.created_at.isoformat(),
        updated_at=model.updated_at.isoformat(),
        meta_info=model.meta_info or {},
    )


def models_to_client_schemas(models: list[ClientModel]) -> list[Client]:
    """
    Convert a list of ClientModel instances to Client schemas.

    Args:
        models: List of ClientModel instances

    Returns:
        List of Client schema instances
    """
    return [model_to_client_schema(model) for model in models if model is not None]


def document_type_enum_to_schema(enum_value: DocumentTypeEnum) -> DocumentType:
    """
    Convert DocumentTypeEnum to DocumentType schema.

    Args:
        enum_value: DocumentTypeEnum value

    Returns:
        DocumentType schema value
    """
    return DocumentType(enum_value.value)


def gender_type_enum_to_schema(enum_value: GenderTypeEnum) -> GenderType:
    """
    Convert GenderTypeEnum to GenderType schema.

    Args:
        enum_value: GenderTypeEnum value

    Returns:
        GenderType schema value
    """
    return GenderType(enum_value.value)


def document_type_schema_to_enum(schema_value: DocumentType) -> DocumentTypeEnum:
    """
    Convert DocumentType schema to DocumentTypeEnum.

    Args:
        schema_value: DocumentType schema value

    Returns:
        DocumentTypeEnum value
    """
    return DocumentTypeEnum[schema_value.value]


def gender_type_schema_to_enum(schema_value: GenderType) -> GenderTypeEnum:
    """
    Convert GenderType schema to GenderTypeEnum.

    Args:
        schema_value: GenderType schema value

    Returns:
        GenderTypeEnum value
    """
    return GenderTypeEnum[schema_value.value.upper()]


def model_to_user_schema(model: "UserModel") -> "User":
    """
    Convert UserModel to User schema.

    Args:
        model: UserModel instance from database

    Returns:
        User schema instance

    Raises:
        ValueError: If model is None or invalid
    """
    if model is None:
        raise ValueError("UserModel cannot be None")

    from app.schemas.user import User, UserRole

    return User(
        username=model.username,
        email=model.email,
        full_name=model.full_name,
        role=UserRole(model.role.value),
        disabled=model.disabled,
    )


def model_to_user_in_db_schema(model: UserModel) -> "UserInDB":
    """
    Convert UserModel to UserInDB schema.

    Args:
        model: UserModel instance from database

    Returns:
        UserInDB schema instance

    Raises:
        ValueError: If model is None or invalid
    """
    if model is None:
        raise ValueError("UserModel cannot be None")

    from app.schemas.user import UserInDB, UserRole

    return UserInDB(
        username=model.username,
        email=model.email,
        full_name=model.full_name,
        role=UserRole(model.role.value),
        disabled=model.disabled,
        hashed_password=model.hashed_password,
    )

