"""
Human face validation utilities for face recognition.

This module provides validation capabilities to ensure detected faces are
valid human faces with appropriate characteristics. It validates age, gender,
facial landmarks, face angle, and face size to ensure registration quality.
"""

import logging
from typing import Tuple, Optional, Any
import numpy as np

from app.core.config import settings
from app.core.constants import (
    ERROR_INVALID_HUMAN_FACE,
    ERROR_INVALID_FACE_ANGLE,
    ERROR_FACE_TOO_SMALL,
)

logger = logging.getLogger(__name__)


class HumanFaceValidator:
    """
    Validates human face characteristics.
    
    This class provides methods to validate that detected faces meet
    requirements for human face characteristics including age, gender,
    landmarks, angle, and size.
    """
    
    @staticmethod
    def validate_face_characteristics(face: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate human face characteristics from InsightFace face object.
        
        Checks age, gender, and landmarks to ensure it's a valid human face.
        
        Args:
            face: InsightFace Face object with detected face data
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
            - is_valid: True if face characteristics are valid
            - error_message: Error message if validation fails, None otherwise
        """
        try:
            # Validate age if available
            if hasattr(face, 'age'):
                age = int(face.age)
                min_age = settings.FACE_VALIDATION_MIN_AGE
                max_age = settings.FACE_VALIDATION_MAX_AGE
                
                if age < min_age or age > max_age:
                    logger.warning(
                        f"Invalid age detected: {age} (expected {min_age}-{max_age})"
                    )
                    return False, f"{ERROR_INVALID_HUMAN_FACE}. Edad detectada fuera del rango válido ({age} años)"
            
            # Validate gender if available
            # InsightFace gender: 1 = Male, 0 = Female
            if hasattr(face, 'gender'):
                gender = face.gender
                if gender not in [0, 1]:
                    logger.warning(f"Invalid gender value: {gender}")
                    return False, f"{ERROR_INVALID_HUMAN_FACE}. Género no válido"
            
            # Validate landmarks if available
            if hasattr(face, 'kps'):
                landmarks = face.kps
                if landmarks is None or len(landmarks) < 5:
                    logger.warning(f"Invalid landmarks: {landmarks}")
                    return False, f"{ERROR_INVALID_HUMAN_FACE}. Landmarks faciales insuficientes"
            
            logger.debug("Face characteristics validation passed")
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating face characteristics: {e}", exc_info=True)
            return False, f"{ERROR_INVALID_HUMAN_FACE}. Error en la validación"

    @staticmethod
    def check_face_angle(face: Any, image_shape: Tuple[int, int]) -> Tuple[bool, Optional[str]]:
        """
        Validate that face is frontal (not extreme profile).
        
        Calculates face angle from landmarks and ensures it's within acceptable range.
        
        Args:
            face: InsightFace Face object with detected face data
            image_shape: Tuple of (height, width) of the image
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        try:
            if not hasattr(face, 'kps') or face.kps is None:
                logger.warning("Landmarks not available for angle calculation")
                # If landmarks not available, use bounding box as fallback
                return HumanFaceValidator._check_face_angle_from_bbox(face, image_shape)
            
            landmarks = face.kps
            if len(landmarks) < 5:
                logger.warning("Insufficient landmarks for angle calculation")
                return HumanFaceValidator._check_face_angle_from_bbox(face, image_shape)
            
            # Calculate face angle from landmarks
            # Use eye positions to estimate angle
            # InsightFace landmarks: [left_eye, right_eye, nose, left_mouth, right_mouth]
            left_eye = landmarks[0]
            right_eye = landmarks[1]
            
            # Calculate angle from horizontal
            dx = right_eye[0] - left_eye[0]
            dy = right_eye[1] - left_eye[1]
            
            # Calculate angle in degrees
            angle_rad = np.arctan2(abs(dy), abs(dx))
            angle_deg = np.degrees(angle_rad)
            
            # Also check for vertical tilt
            nose = landmarks[2] if len(landmarks) > 2 else None
            if nose is not None:
                # Check vertical alignment
                eye_center_y = (left_eye[1] + right_eye[1]) / 2
                vertical_offset = abs(nose[1] - eye_center_y)
                eye_distance = np.sqrt(dx**2 + dy**2)
                
                if eye_distance > 0:
                    vertical_tilt = np.degrees(np.arctan2(vertical_offset, eye_distance))
                    angle_deg = max(angle_deg, vertical_tilt)
            
            max_angle = settings.FACE_VALIDATION_MAX_FACE_ANGLE
            
            if angle_deg > max_angle:
                logger.warning(
                    f"Face angle too large: {angle_deg:.2f}° (max: {max_angle}°)"
                )
                return False, ERROR_INVALID_FACE_ANGLE
            
            logger.debug(f"Face angle validation passed: {angle_deg:.2f}°")
            return True, None
            
        except Exception as e:
            logger.error(f"Error checking face angle: {e}", exc_info=True)
            # Fail open: don't block if angle calculation fails
            return True, None

    @staticmethod
    def _check_face_angle_from_bbox(face: Any, image_shape: Tuple[int, int]) -> Tuple[bool, Optional[str]]:
        """
        Fallback method to check face angle from bounding box.
        
        Args:
            face: InsightFace Face object
            image_shape: Tuple of (height, width)
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        try:
            bbox = face.bbox
            bbox_width = bbox[2] - bbox[0]
            bbox_height = bbox[3] - bbox[1]
            
            # Check aspect ratio (extreme ratios suggest profile)
            aspect_ratio = bbox_width / bbox_height if bbox_height > 0 else 1.0
            
            # Normal face should have aspect ratio close to 1.0
            # Profile faces have extreme ratios
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                logger.warning(f"Extreme aspect ratio suggests profile: {aspect_ratio:.2f}")
                return False, ERROR_INVALID_FACE_ANGLE
            
            return True, None
        except Exception as e:
            logger.debug(f"Error in bbox angle check: {e}")
            return True, None

    @staticmethod
    def validate_face_size(face: Any, image_shape: Tuple[int, int]) -> Tuple[bool, Optional[str]]:
        """
        Validate that face is large enough in the image.
        
        Args:
            face: InsightFace Face object with detected face data
            image_shape: Tuple of (height, width) of the image
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        try:
            bbox = face.bbox
            face_width = bbox[2] - bbox[0]
            face_height = bbox[3] - bbox[1]
            face_area = face_width * face_height
            
            image_height, image_width = image_shape[:2]
            image_area = image_height * image_width
            
            face_ratio = face_area / image_area if image_area > 0 else 0.0
            
            min_ratio = settings.FACE_VALIDATION_MIN_FACE_SIZE_RATIO
            
            if face_ratio < min_ratio:
                logger.warning(
                    f"Face too small: ratio={face_ratio:.4f} (min: {min_ratio:.4f})"
                )
                return False, ERROR_FACE_TOO_SMALL
            
            logger.debug(f"Face size validation passed: ratio={face_ratio:.4f}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating face size: {e}", exc_info=True)
            return False, ERROR_FACE_TOO_SMALL

    @staticmethod
    def check_face_landmarks(face: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate that facial landmarks are present and well-distributed.
        
        Args:
            face: InsightFace Face object with detected face data
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        try:
            if not hasattr(face, 'kps') or face.kps is None:
                logger.warning("Landmarks not available")
                return False, f"{ERROR_INVALID_HUMAN_FACE}. Landmarks faciales no disponibles"
            
            landmarks = face.kps
            if len(landmarks) < 5:
                logger.warning(f"Insufficient landmarks: {len(landmarks)}")
                return False, f"{ERROR_INVALID_HUMAN_FACE}. Landmarks faciales insuficientes ({len(landmarks)})"
            
            # Check that landmarks are well-distributed
            # Calculate spread of landmarks
            landmarks_array = np.array(landmarks)
            x_coords = landmarks_array[:, 0]
            y_coords = landmarks_array[:, 1]
            
            x_spread = np.max(x_coords) - np.min(x_coords)
            y_spread = np.max(y_coords) - np.min(y_coords)
            
            # If spread is too small, landmarks might be incorrect
            if x_spread < 10 or y_spread < 10:
                logger.warning(
                    f"Landmarks too clustered: x_spread={x_spread:.2f}, "
                    f"y_spread={y_spread:.2f}"
                )
                return False, f"{ERROR_INVALID_HUMAN_FACE}. Landmarks mal distribuidos"
            
            logger.debug("Face landmarks validation passed")
            return True, None
            
        except Exception as e:
            logger.error(f"Error checking face landmarks: {e}", exc_info=True)
            return False, f"{ERROR_INVALID_HUMAN_FACE}. Error validando landmarks"

    @staticmethod
    def validate_face(
        face: Any,
        image_shape: Tuple[int, int]
    ) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive face validation combining all checks.
        
        Args:
            face: InsightFace Face object with detected face data
            image_shape: Tuple of (height, width) of the image
            
        Returns:
            Tuple of (is_valid: bool, error_message: Optional[str])
        """
        # Validate characteristics
        is_valid, error = HumanFaceValidator.validate_face_characteristics(face)
        if not is_valid:
            return False, error
        
        # Validate face size
        is_valid, error = HumanFaceValidator.validate_face_size(face, image_shape)
        if not is_valid:
            return False, error
        
        # Validate face angle
        is_valid, error = HumanFaceValidator.check_face_angle(face, image_shape)
        if not is_valid:
            return False, error
        
        # Validate landmarks
        is_valid, error = HumanFaceValidator.check_face_landmarks(face)
        if not is_valid:
            return False, error
        
        logger.debug("Comprehensive face validation passed")
        return True, None

