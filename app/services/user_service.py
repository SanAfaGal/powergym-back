"""
User service for PowerGym API.

This module provides business logic for user management operations,
including authentication, authorization, and user CRUD operations.
"""

from typing import List, Optional
import logging

from sqlalchemy.orm import Session

from app.schemas.user import User, UserCreate, UserInDB, UserUpdate, UserRole
from app.core.security import get_password_hash, verify_password
from app.core.config import settings
from app.repositories.user_repository import UserRepository
from app.db.models import UserModel, UserRoleEnum
from app.utils.mappers import model_to_user_schema, model_to_user_in_db_schema
from app.utils.exceptions import NotFoundError, ConflictError, InternalServerError

logger = logging.getLogger(__name__)


class UserService:
    """
    Service for user-related business logic.

    Handles user authentication, authorization, and all CRUD operations
    for user management.
    """

    @staticmethod
    def initialize_super_admin(db: Session) -> None:
        """
        Initialize the super admin user on application startup.
        """
        try:
            existing_user = UserRepository.get_by_username(
                db, settings.SUPER_ADMIN_USERNAME
            )

            if not existing_user:
                hashed_password = get_password_hash(settings.SUPER_ADMIN_PASSWORD)
                try: # << NUEVO TRY/EXCEPT PARA CONCURRENCIA
                    UserRepository.create(
                        db=db,
                        username=settings.SUPER_ADMIN_USERNAME,
                        email=settings.SUPER_ADMIN_EMAIL,
                        full_name=settings.SUPER_ADMIN_FULL_NAME,
                        hashed_password=hashed_password,
                        role=UserRoleEnum.ADMIN,
                        disabled=False,
                    )
                    logger.info("Super admin user created successfully")
                except IntegrityError:
                    # Esto atrapa el caso de concurrencia. Otro worker acaba de crear el usuario.
                    db.rollback() # Es CRÍTICO hacer rollback si ocurre un error de DB
                    logger.debug("Super admin user already exists (concurrency handled)")
                except Exception as e:
                    # Cualquier otro error durante la creación
                    db.rollback()
                    raise e
            else:
                logger.debug("Super admin user already exists")

        except Exception as e:
            # Este es el bloque de manejo de errores original.
            logger.error(
                "Error initializing super admin: %s", str(e), exc_info=True
            )
            # No se hace raise - se permite que la app inicie
            
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[UserInDB]:
        """
        Retrieve a user by their username.

        Args:
            db: Database session
            username: Username to search for

        Returns:
            UserInDB schema instance if found, None otherwise
        """
        try:
            user_model = UserRepository.get_by_username(db, username)
            if user_model:
                return model_to_user_in_db_schema(user_model)
            return None

        except Exception as e:
            logger.error(
                "Error retrieving user by username '%s': %s",
                username,
                str(e),
                exc_info=True,
            )
            raise InternalServerError(
                detail=f"Failed to retrieve user: {str(e)}"
            ) from e

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[UserInDB]:
        """
        Retrieve a user by their email address.

        Args:
            db: Database session
            email: Email address to search for

        Returns:
            UserInDB schema instance if found, None otherwise
        """
        try:
            user_model = UserRepository.get_by_email(db, email)
            if user_model:
                return model_to_user_in_db_schema(user_model)
            return None

        except Exception as e:
            logger.error(
                "Error retrieving user by email '%s': %s",
                email,
                str(e),
                exc_info=True,
            )
            raise InternalServerError(
                detail=f"Failed to retrieve user: {str(e)}"
            ) from e

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Create a new user account.

        Args:
            db: Database session
            user_data: User creation data

        Returns:
            Created User schema instance

        Raises:
            ConflictError: If username or email already exists
            InternalServerError: If user creation fails
        """
        try:
            hashed_password = get_password_hash(user_data.password)

            role_enum = (
                UserRoleEnum.ADMIN
                if user_data.role == UserRole.ADMIN
                else UserRoleEnum.EMPLOYEE
            )

            user_model = UserRepository.create(
                db=db,
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                hashed_password=hashed_password,
                role=role_enum,
                disabled=False,
            )

            logger.info("User created successfully: %s", user_data.username)
            return model_to_user_schema(user_model)

        except Exception as e:
            logger.error(
                "Error creating user '%s': %s", user_data.username, str(e), exc_info=True
            )
            raise InternalServerError(
                detail=f"Failed to create user: {str(e)}"
            ) from e

    @staticmethod
    def update_user(
        db: Session, username: str, user_update: UserUpdate
    ) -> Optional[User]:
        """
        Update an existing user's information.

        Args:
            db: Database session
            username: Username of the user to update
            user_update: User update data

        Returns:
            Updated User schema instance if found, None otherwise

        Raises:
            InternalServerError: If update fails
        """
        try:
            update_dict = {}
            if user_update.email is not None:
                update_dict["email"] = user_update.email
            if user_update.full_name is not None:
                update_dict["full_name"] = user_update.full_name

            if not update_dict:
                # No updates provided, return current user
                return UserService.get_user_by_username(db, username)

            user_model = UserRepository.update(db, username, **update_dict)

            if user_model:
                logger.info("User updated successfully: %s", username)
                return model_to_user_schema(user_model)

            return None

        except Exception as e:
            logger.error(
                "Error updating user '%s': %s", username, str(e), exc_info=True
            )
            raise InternalServerError(
                detail=f"Failed to update user: {str(e)}"
            ) from e

    @staticmethod
    def change_password(db: Session, username: str, new_password: str) -> bool:
        """
        Change a user's password.

        Args:
            db: Database session
            username: Username of the user
            new_password: New password (will be hashed)

        Returns:
            True if password was changed successfully, False otherwise

        Raises:
            InternalServerError: If password change fails
        """
        try:
            hashed_password = get_password_hash(new_password)
            user_model = UserRepository.update(
                db, username, hashed_password=hashed_password
            )

            if user_model:
                logger.info("Password changed successfully for user: %s", username)
                return True

            return False

        except Exception as e:
            logger.error(
                "Error changing password for user '%s': %s",
                username,
                str(e),
                exc_info=True,
            )
            raise InternalServerError(
                detail=f"Failed to change password: {str(e)}"
            ) from e

    @staticmethod
    def disable_user(db: Session, username: str) -> Optional[User]:
        """
        Disable a user account (soft delete).

        Args:
            db: Database session
            username: Username of the user to disable

        Returns:
            Updated User schema instance if found, None otherwise

        Raises:
            InternalServerError: If disable operation fails
        """
        try:
            user_model = UserRepository.update(db, username, disabled=True)
            if user_model:
                logger.info("User disabled successfully: %s", username)
                return model_to_user_schema(user_model)
            return None

        except Exception as e:
            logger.error(
                "Error disabling user '%s': %s", username, str(e), exc_info=True
            )
            raise InternalServerError(
                detail=f"Failed to disable user: {str(e)}"
            ) from e

    @staticmethod
    def enable_user(db: Session, username: str) -> Optional[User]:
        """
        Enable a previously disabled user account.

        Args:
            db: Database session
            username: Username of the user to enable

        Returns:
            Updated User schema instance if found, None otherwise

        Raises:
            InternalServerError: If enable operation fails
        """
        try:
            user_model = UserRepository.update(db, username, disabled=False)
            if user_model:
                logger.info("User enabled successfully: %s", username)
                return model_to_user_schema(user_model)
            return None

        except Exception as e:
            logger.error(
                "Error enabling user '%s': %s", username, str(e), exc_info=True
            )
            raise InternalServerError(
                detail=f"Failed to enable user: {str(e)}"
            ) from e

    @staticmethod
    def change_user_role(
        db: Session, username: str, new_role: UserRole
    ) -> Optional[User]:
        """
        Change a user's role.

        Args:
            db: Database session
            username: Username of the user
            new_role: New role to assign

        Returns:
            Updated User schema instance if found, None otherwise

        Raises:
            InternalServerError: If role change fails
        """
        try:
            role_enum = (
                UserRoleEnum.ADMIN
                if new_role == UserRole.ADMIN
                else UserRoleEnum.EMPLOYEE
            )
            user_model = UserRepository.update(db, username, role=role_enum)

            if user_model:
                logger.info(
                    "User role changed successfully for '%s': %s",
                    username,
                    new_role.value,
                )
                return model_to_user_schema(user_model)

            return None

        except Exception as e:
            logger.error(
                "Error changing role for user '%s': %s",
                username,
                str(e),
                exc_info=True,
            )
            raise InternalServerError(
                detail=f"Failed to change user role: {str(e)}"
            ) from e

    @staticmethod
    def delete_user(db: Session, username: str) -> bool:
        """
        Delete a user account (hard delete).

        Args:
            db: Database session
            username: Username of the user to delete

        Returns:
            True if deletion was successful, False otherwise

        Raises:
            InternalServerError: If deletion fails
        """
        try:
            result = UserRepository.delete(db, username)
            if result:
                logger.info("User deleted successfully: %s", username)
            return result

        except Exception as e:
            logger.error(
                "Error deleting user '%s': %s", username, str(e), exc_info=True
            )
            raise InternalServerError(
                detail=f"Failed to delete user: {str(e)}"
            ) from e

    @staticmethod
    def get_all_users(db: Session) -> List[User]:
        """
        Retrieve all users in the system.

        Args:
            db: Database session

        Returns:
            List of User schema instances

        Raises:
            InternalServerError: If retrieval fails
        """
        try:
            user_models = UserRepository.get_all(db)
            return [model_to_user_schema(user) for user in user_models if user]

        except Exception as e:
            logger.error("Error retrieving all users: %s", str(e), exc_info=True)
            raise InternalServerError(
                detail=f"Failed to retrieve users: {str(e)}"
            ) from e

    @staticmethod
    def authenticate_user(
        db: Session, username: str, password: str
    ) -> Optional[UserInDB]:
        """
        Authenticate a user with username and password.

        Args:
            db: Database session
            username: Username to authenticate
            password: Plain text password

        Returns:
            UserInDB schema instance if authentication succeeds, None otherwise
        """
        try:
            user = UserService.get_user_by_username(db, username)
            if not user:
                logger.warning("Authentication failed: user '%s' not found", username)
                return None

            if not verify_password(password, user.hashed_password):
                logger.warning(
                    "Authentication failed: incorrect password for user '%s'", username
                )
                return None

            logger.info("User authenticated successfully: %s", username)
            return user

        except Exception as e:
            logger.error(
                "Error authenticating user '%s': %s",
                username,
                str(e),
                exc_info=True,
            )
            # Don't raise - return None to indicate authentication failure
            return None
