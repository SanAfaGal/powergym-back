"""
Image processing utilities for face recognition.

This module handles image decoding, validation, compression, and thumbnail
generation for face recognition operations.
"""

import base64
import io
import logging
from typing import Tuple, Optional
import numpy as np
from PIL import Image

from app.core.config import settings
from app.core.compression import CompressionService

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Handles all image processing operations for face recognition."""

    @staticmethod
    def validate_image_size(image_data: bytes) -> None:
        """
        Validate that image size is within allowed limits.

        Args:
            image_data: Raw image bytes

        Raises:
            ValueError: If image exceeds maximum allowed size
        """
        max_size_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
        image_size_mb = len(image_data) / (1024 * 1024)
        
        if len(image_data) > max_size_bytes:
            error_msg = (
                f"Image size ({image_size_mb:.2f}MB) exceeds maximum allowed size "
                f"of {settings.MAX_IMAGE_SIZE_MB}MB"
            )
            logger.warning(error_msg)
            raise ValueError(error_msg)
        
        logger.debug(f"Image size validation passed: {image_size_mb:.2f}MB")

    @staticmethod
    def decode_base64_image(image_base64: str) -> np.ndarray:
        """
        Decode base64 image string to numpy array.

        Args:
            image_base64: Base64 encoded image string (with or without data URI prefix)

        Returns:
            Image as numpy array in RGB format

        Raises:
            ValueError: If image format is invalid, size exceeds limit, or decoding fails
        """
        try:
            logger.debug("Decoding base64 image")
            
            # Remove data URI prefix if present
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]

            image_bytes = base64.b64decode(image_base64)
            ImageProcessor.validate_image_size(image_bytes)

            image = Image.open(io.BytesIO(image_bytes))
            image_format = image.format.lower() if image.format else 'unknown'
            allowed_formats_lower = [fmt.lower() for fmt in settings.ALLOWED_IMAGE_FORMATS]

            if image_format not in allowed_formats_lower:
                error_msg = (
                    f"Invalid image format '{image_format}'. "
                    f"Allowed formats: {settings.ALLOWED_IMAGE_FORMATS}"
                )
                logger.warning(error_msg)
                raise ValueError(error_msg)

            image_rgb = image.convert('RGB')
            image_array = np.array(image_rgb)
            
            logger.debug(f"Successfully decoded image: format={image_format}, size={image_array.shape}")
            return image_array

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to decode image: {e}", exc_info=True)
            raise ValueError(f"Failed to decode image: {str(e)}") from e

    @staticmethod
    def create_thumbnail(
        image_array: np.ndarray,
        size: Optional[Tuple[int, int]] = None
    ) -> bytes:
        """
        Create a thumbnail from an image array.

        Args:
            image_array: Image as numpy array in RGB format
            size: Optional thumbnail dimensions (width, height).
                  If None, uses default from settings

        Returns:
            Thumbnail image as JPEG bytes

        Raises:
            ValueError: If thumbnail creation fails
        """
        try:
            if size is None:
                size = (settings.THUMBNAIL_WIDTH, settings.THUMBNAIL_HEIGHT)
            
            logger.debug(f"Creating thumbnail with size {size}")
            thumbnail = CompressionService.compress_thumbnail(image_array, size=size)
            logger.debug(f"Thumbnail created successfully: {len(thumbnail)} bytes")
            return thumbnail
        except Exception as e:
            logger.error(f"Failed to create thumbnail: {e}", exc_info=True)
            raise ValueError(f"Failed to create thumbnail: {str(e)}") from e

    @staticmethod
    def compress_image(image_array: np.ndarray, quality: Optional[int] = None) -> bytes:
        """
        Compress an image array to JPEG format.

        Args:
            image_array: Image as numpy array in RGB format
            quality: Optional JPEG quality (1-100).
                    If None, uses default from settings

        Returns:
            Compressed image as JPEG bytes

        Raises:
            ValueError: If compression fails
        """
        try:
            if quality is None:
                quality = settings.IMAGE_COMPRESSION_QUALITY
            
            logger.debug(f"Compressing image with quality {quality}")
            compressed = CompressionService.compress_image(image_array, quality=quality)
            logger.debug(f"Image compressed successfully: {len(compressed)} bytes")
            return compressed
        except Exception as e:
            logger.error(f"Failed to compress image: {e}", exc_info=True)
            raise ValueError(f"Failed to compress image: {str(e)}") from e
