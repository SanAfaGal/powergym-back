"""
Face recognition API endpoints.

This module provides REST API endpoints for face recognition operations,
including registration, authentication, comparison, update, and deletion.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.schemas.face_recognition import (
    FaceAuthenticationRequest,
    FaceAuthenticationResponse,
    FaceComparisonRequest,
    FaceComparisonResponse,
    FaceDeleteResponse,
    FaceRegistrationRequest,
    FaceRegistrationResponse,
    FaceUpdateRequest,
)
from app.schemas.user import User
from app.services.client_service import ClientService
from app.services.face_recognition.core import FaceRecognitionService

logger = logging.getLogger(__name__)

router = APIRouter()


def _validate_client_active(db: Session, client_id: UUID) -> None:
    """
    Validate that a client exists and is active.
    
    Args:
        db: Database session
        client_id: UUID of the client to validate
        
    Raises:
        HTTPException: If client not found (404), not active (400), or database error (500)
    """
    try:
        logger.debug(f"Validating client {client_id} exists and is active")
        client = ClientService.get_client_by_id(db, client_id)
        
        if not client:
            logger.warning(f"Client not found: {client_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )

        if not client.is_active:
            logger.warning(f"Client is not active: {client_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client is not active"
            )
        
        logger.debug(f"Client {client_id} validation passed: exists and is active")
        
    except HTTPException:
        # Re-raise HTTPException as-is
        raise
    except Exception as e:
        # Catch any other exceptions (e.g., database errors)
        logger.error(
            f"Error validating client {client_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while validating client. Please try again later."
        )

@router.post(
    "/register",
    response_model=FaceRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register face biometric",
    description="Register a client's face biometric data for facial recognition.",
    responses={
        201: {
            "description": "Face registered successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Face registered successfully",
                        "biometric_id": "123e4567-e89b-12d3-a456-426614174000",
                        "client_id": "987fcdeb-51a2-43f1-9876-543210fedcba"
                    }
                }
            }
        },
        400: {"description": "Invalid image or no face detected"},
        404: {"description": "Client not found"},
        401: {"description": "Not authenticated"}
    }
)
def register_client_face(
    request: FaceRegistrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FaceRegistrationResponse:
    """
    Register a client's face biometric data.
    
    Args:
        request: Face registration request with client_id and image_base64
        current_user: Authenticated user (from dependency)
        db: Database session (from dependency)
        
    Returns:
        FaceRegistrationResponse with success status and biometric information
        
    Raises:
        HTTPException: If client validation fails or registration fails
    """
    logger.info(f"Face registration requested for client {request.client_id} by user {current_user.username}")
    _validate_client_active(db, request.client_id)

    result = FaceRecognitionService.register_face(
        db=db,
        client_id=request.client_id,
        image_base64=request.image_base64
    )

    if not result.get("success"):
        error_msg = result.get("error", "Failed to register face")
        logger.error(f"Face registration failed for client {request.client_id}: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    logger.info(f"Face registered successfully for client {request.client_id}")
    return FaceRegistrationResponse(
        success=True,
        message="Face registered successfully",
        biometric_id=result.get("biometric_id"),
        client_id=result.get("client_id")
    )

@router.post(
    "/authenticate",
    response_model=FaceAuthenticationResponse,
    summary="Authenticate with face",
    description="Authenticate a client by comparing their face with registered biometrics.",
    responses={
        200: {
            "description": "Face authenticated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Face authenticated successfully",
                        "client_id": "987fcdeb-51a2-43f1-9876-543210fedcba",
                        "client_info": {
                            "first_name": "Juan",
                            "last_name": "Pérez",
                            "dni_number": "12345678"
                        },
                        "confidence": 0.95
                    }
                }
            }
        },
        401: {"description": "Authentication failed - no matching face found"},
        400: {"description": "Invalid image or no face detected"}
    }
)
def authenticate_client_face(
    request: FaceAuthenticationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FaceAuthenticationResponse:
    """
    Authenticate a client by face image.
    
    Args:
        request: Face authentication request with image_base64
        current_user: Authenticated user (from dependency)
        db: Database session (from dependency)
        
    Returns:
        FaceAuthenticationResponse with authentication result and client information
        
    Raises:
        HTTPException: If authentication fails (401) or image processing fails (400)
    """
    logger.info(f"Face authentication requested by user {current_user.username}")
    result = FaceRecognitionService.authenticate_face(
        db=db,
        image_base64=request.image_base64
    )

    if not result.get("success"):
        error_msg = result.get("error", "Authentication failed")
        logger.warning(f"Face authentication failed: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_msg
        )

    logger.info(f"Face authenticated successfully for client {result.get('client_id')}")
    return FaceAuthenticationResponse(
        success=True,
        message="Face authenticated successfully",
        client_id=result.get("client_id"),
        client_info=result.get("client_info"),
        confidence=result.get("confidence")
    )

@router.post(
    "/compare",
    response_model=FaceComparisonResponse,
    summary="Compare two faces",
    description="Compare two face images to determine if they belong to the same person.",
    responses={
        200: {
            "description": "Faces compared successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Faces compared successfully",
                        "match": True,
                        "distance": 0.35,
                        "confidence": 0.92
                    }
                }
            }
        },
        400: {"description": "Invalid images or no faces detected"},
        401: {"description": "Not authenticated"}
    }
)
def compare_faces(
    request: FaceComparisonRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FaceComparisonResponse:
    """
    Compare two face images to determine if they belong to the same person.
    
    Args:
        request: Face comparison request with two image_base64 strings
        current_user: Authenticated user (from dependency)
        db: Database session (from dependency)
        
    Returns:
        FaceComparisonResponse with comparison result and confidence scores
        
    Raises:
        HTTPException: If image processing fails or comparison fails (400)
    """
    logger.info(f"Face comparison requested by user {current_user.username}")
    result = FaceRecognitionService.compare_two_faces(
        image_base64_1=request.image_base64_1,
        image_base64_2=request.image_base64_2
    )

    if not result.get("success"):
        error_msg = result.get("error", "Failed to compare faces")
        logger.error(f"Face comparison failed: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    logger.info(f"Face comparison completed: match={result.get('match')}, confidence={result.get('confidence'):.4f}")
    return FaceComparisonResponse(
        success=True,
        message="Faces compared successfully",
        match=result.get("match"),
        distance=result.get("distance"),
        confidence=result.get("confidence")
    )

@router.put(
    "/update",
    response_model=FaceRegistrationResponse,
    summary="Update face biometric",
    description="Update a client's face biometric data with a new image.",
    responses={
        200: {
            "description": "Face updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Face updated successfully",
                        "biometric_id": "123e4567-e89b-12d3-a456-426614174000",
                        "client_id": "987fcdeb-51a2-43f1-9876-543210fedcba"
                    }
                }
            }
        },
        400: {"description": "Invalid image or no face detected"},
        404: {"description": "Client not found"},
        401: {"description": "Not authenticated"}
    }
)
def update_client_face(
    request: FaceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FaceRegistrationResponse:
    """
    Update a client's face biometric data with a new image.
    
    Args:
        request: Face update request with client_id and image_base64
        current_user: Authenticated user (from dependency)
        db: Database session (from dependency)
        
    Returns:
        FaceRegistrationResponse with success status and updated biometric information
        
    Raises:
        HTTPException: If client validation fails or update fails
    """
    # Extract and validate request data
    try:
        client_id = request.client_id
        user_id = current_user.username
        image_base64 = request.image_base64
        image_size = len(image_base64) if image_base64 else 0
        
        logger.info(
            f"Face update requested - client_id: {client_id}, user_id: {user_id}, "
            f"image_size: {image_size} bytes, client_id_type: {type(client_id)}"
        )
        
        # Validate client_id is not None
        if client_id is None:
            logger.error("client_id is None in request")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="client_id is required"
            )
        
        # Validate image_base64 is not None or empty
        if not image_base64 or len(image_base64.strip()) == 0:
            logger.error(f"image_base64 is empty for client {client_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="image_base64 cannot be empty"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting request data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request data: {str(e)}"
        )
    
    try:
        # Validate client exists and is active
        logger.debug(f"Validating client {client_id} is active")
        _validate_client_active(db, client_id)
        logger.debug(f"Client {client_id} validation passed")

        # Update face biometric
        logger.debug(f"Calling FaceRecognitionService.update_face for client {client_id}")
        result = FaceRecognitionService.update_face(
            db=db,
            client_id=client_id,
            image_base64=image_base64
        )
        logger.debug(f"FaceRecognitionService.update_face returned result: {result}")

        # Validate result structure
        if not isinstance(result, dict):
            error_msg = f"Invalid result type from update_face: {type(result)}"
            logger.error(f"Face update failed for client {client_id}: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error: Invalid response from face recognition service"
            )

        # Check if update was successful
        if not result.get("success"):
            error_msg = result.get("error", "Failed to update face")
            logger.error(
                f"Face update failed for client {client_id} by user {user_id}: {error_msg}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # Validate and extract result values
        biometric_id_str = result.get("biometric_id")
        client_id_str = result.get("client_id")
        
        if not biometric_id_str:
            logger.error(
                f"Face update succeeded but biometric_id is missing in result for client {client_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error: Missing biometric_id in response"
            )
        
        if not client_id_str:
            logger.error(
                f"Face update succeeded but client_id is missing in result for client {client_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error: Missing client_id in response"
            )

        # Convert string UUIDs to UUID objects
        try:
            biometric_id = UUID(biometric_id_str) if isinstance(biometric_id_str, str) else biometric_id_str
            result_client_id = UUID(client_id_str) if isinstance(client_id_str, str) else client_id_str
        except (ValueError, TypeError) as e:
            logger.error(
                f"Invalid UUID format in result for client {client_id}: "
                f"biometric_id={biometric_id_str}, client_id={client_id_str}, error={e}",
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error: Invalid UUID format in response"
            )

        # Verify client_id matches
        if result_client_id != client_id:
            logger.warning(
                f"Client ID mismatch: requested {client_id}, got {result_client_id}"
            )

        logger.info(
            f"Face updated successfully for client {client_id} by user {user_id}, "
            f"biometric_id: {biometric_id}"
        )
        
        return FaceRegistrationResponse(
            success=True,
            message="Face updated successfully",
            biometric_id=biometric_id,
            client_id=result_client_id
        )
        
    except HTTPException:
        # Re-raise HTTPException as-is (already properly formatted)
        raise
    except ValueError as ve:
        # Handle validation errors
        logger.error(
            f"Validation error updating face for client {client_id} by user {user_id}: {ve}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(ve)}"
        )
    except Exception as e:
        # Catch all other exceptions and return 500
        logger.error(
            f"Unexpected error updating face for client {client_id} by user {user_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred while updating face biometric. Please try again later."
        )

@router.delete(
    "/{client_id}",
    response_model=FaceDeleteResponse,
    summary="Delete face biometric",
    description="Delete all face biometric data for a specific client.",
    responses={
        200: {
            "description": "Face biometric deleted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Face biometric deleted successfully"
                    }
                }
            }
        },
        404: {"description": "Client not found"},
        400: {"description": "Failed to delete face biometric"},
        401: {"description": "Not authenticated"}
    }
)
def delete_client_face(
    client_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FaceDeleteResponse:
    """
    Delete all face biometric data for a specific client.
    
    Args:
        client_id: UUID of the client whose face biometrics should be deleted
        current_user: Authenticated user (from dependency)
        db: Database session (from dependency)
        
    Returns:
        FaceDeleteResponse with success status
        
    Raises:
        HTTPException: If client not found (404) or deletion fails (400)
    """
    logger.info(f"Face deletion requested for client {client_id} by user {current_user.username}")
    
    client = ClientService.get_client_by_id(db, client_id)
    if not client:
        logger.warning(f"Client not found for face deletion: {client_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    result = FaceRecognitionService.delete_face(db=db, client_id=client_id)

    if not result.get("success"):
        error_msg = result.get("error", "Failed to delete face biometric")
        logger.error(f"Face deletion failed for client {client_id}: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    logger.info(f"Face biometric deleted successfully for client {client_id}")
    return FaceDeleteResponse(
        success=True,
        message="Face biometric deleted successfully"
    )
