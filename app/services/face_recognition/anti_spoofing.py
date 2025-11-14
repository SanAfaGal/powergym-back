"""
Anti-spoofing detection utilities for face recognition.

This module provides liveness detection capabilities to prevent photo and screen
attacks during face registration. It uses computer vision techniques to analyze
texture, depth, reflections, and other characteristics that distinguish real
faces from photos or screens.
"""

import logging
from typing import Tuple, Optional
import numpy as np
import cv2

from app.core.config import settings
from app.core.constants import (
    ERROR_PHOTO_ATTACK_DETECTED,
    ERROR_SCREEN_ATTACK_DETECTED,
    ERROR_PHONE_SCREEN_DETECTED,
)

logger = logging.getLogger(__name__)


class LivenessDetector:
    """
    Detects liveness and prevents photo/screen attacks.
    
    This class provides methods to analyze images for characteristics that
    indicate whether a face is real or from a photo/screen. It uses texture
    analysis, depth detection, reflection analysis, and pixel variation
    to distinguish between real faces and attacks.
    """

    @staticmethod
    def detect_photo_attack(image_array: np.ndarray) -> Tuple[bool, float, Optional[str]]:
        """
        Detect if image is a printed photo attack.
        
        Analyzes texture, depth, and reflections to detect printed photos.
        Printed photos typically have:
        - Different texture patterns (less variation)
        - Flatter appearance (less depth)
        - Different reflection patterns
        
        Args:
            image_array: Image as numpy array in RGB format
            
        Returns:
            Tuple of (is_attack: bool, confidence_score: float, reason: Optional[str])
            - is_attack: True if photo attack is detected
            - confidence_score: Confidence level (0.0-1.0, higher = more confident)
            - reason: Description of why attack was detected (None if no attack)
        """
        try:
            logger.debug("Analyzing image for photo attack")
            
            # Convert to BGR for OpenCV
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            else:
                image_bgr = image_array
                
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            
            # 1. Texture variation analysis
            # Printed photos have less local variation
            texture_score = LivenessDetector._analyze_texture_variation(gray)
            
            # 2. Depth analysis using gradients
            # Real faces have more depth variations
            depth_score = LivenessDetector._analyze_depth_variation(gray)
            
            # 3. Edge detection analysis
            # Printed photos may have different edge patterns
            edge_score = LivenessDetector._analyze_edge_patterns(gray)
            
            # Combine scores (lower = more likely to be photo)
            combined_score = (texture_score + depth_score + edge_score) / 3.0
            
            # Adjust threshold based on image resolution
            # Lower resolution cameras have less variation, so we need to be more lenient
            height, width = gray.shape
            image_resolution = height * width
            resolution_factor = min(image_resolution / 480000.0, 1.0)  # Normalize to 640x480
            
            # More lenient threshold for lower resolution images
            # Base threshold: 0.3 (was 0.5), adjusts up to 0.4 for high-res images
            threshold = 0.3 + (0.1 * resolution_factor)
            
            is_attack = combined_score < threshold
            
            if is_attack:
                logger.warning(
                    f"Photo attack detected: texture={texture_score:.3f}, "
                    f"depth={depth_score:.3f}, edge={edge_score:.3f}, "
                    f"combined={combined_score:.3f}"
                )
                reason = "La textura y profundidad de la imagen sugieren que es una foto impresa"
                return True, 1.0 - combined_score, reason
            
            logger.debug(f"Photo attack check passed: combined_score={combined_score:.3f}")
            return False, combined_score, None
            
        except Exception as e:
            logger.error(f"Error in photo attack detection: {e}", exc_info=True)
            # Fail open: don't block if detection fails
            return False, 0.5, None

    @staticmethod
    def detect_phone_screen(image_array: np.ndarray) -> Tuple[bool, float, Optional[str]]:
        """
        Detect if image is from a phone screen.
        
        Phone screens typically have:
        - Perfect rectangular borders (device edges)
        - Characteristic reflection patterns
        - Pixel grid patterns from screen subpixels
        - Specific brightness patterns
        
        Args:
            image_array: Image as numpy array in RGB format
            
        Returns:
            Tuple of (is_attack: bool, confidence_score: float, reason: Optional[str])
            - is_attack: True if phone screen is detected
            - confidence_score: Confidence level (0.0-1.0)
            - reason: Description of why screen was detected (None if no screen)
        """
        try:
            logger.debug("Analyzing image for phone screen attack")
            
            # Convert to BGR for OpenCV
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            else:
                image_bgr = image_array
                
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape
            
            # 1. Detect perfect rectangular borders (device edges)
            has_rectangular_border = LivenessDetector._detect_rectangular_borders(gray)
            
            # 2. Analyze reflection patterns
            reflection_score = LivenessDetector._analyze_reflection_patterns(gray)
            
            # 3. Analyze pixel grid patterns (subpixel structure)
            grid_score = LivenessDetector._analyze_pixel_grid_patterns(gray)
            
            # 4. Check for screen-like brightness patterns
            brightness_pattern_score = LivenessDetector._analyze_brightness_patterns(gray)
            
            # Combine indicators
            screen_indicators = [
                has_rectangular_border,
                reflection_score < 0.4,  # Low reflection variation suggests screen
                grid_score > 0.6,  # High grid pattern suggests screen
                brightness_pattern_score > 0.6,  # Screen-like brightness pattern
            ]
            
            confidence = sum(screen_indicators) / len(screen_indicators)
            is_attack = confidence > 0.5
            
            if is_attack:
                logger.warning(
                    f"Phone screen detected: border={has_rectangular_border}, "
                    f"reflection={reflection_score:.3f}, grid={grid_score:.3f}, "
                    f"brightness={brightness_pattern_score:.3f}, confidence={confidence:.3f}"
                )
                reason = "Se detectaron características de pantalla de dispositivo móvil"
                return True, confidence, reason
            
            logger.debug(f"Phone screen check passed: confidence={confidence:.3f}")
            return False, 1.0 - confidence, None
            
        except Exception as e:
            logger.error(f"Error in phone screen detection: {e}", exc_info=True)
            # Fail open: don't block if detection fails
            return False, 0.3, None

    @staticmethod
    def detect_screen_attack(image_array: np.ndarray) -> Tuple[bool, float, Optional[str]]:
        """
        Detect if image is from any screen (monitor, tablet, phone).
        
        This is a general screen detection that combines phone screen detection
        with additional checks for other types of screens.
        
        Args:
            image_array: Image as numpy array in RGB format
            
        Returns:
            Tuple of (is_attack: bool, confidence_score: float, reason: Optional[str])
        """
        # First check for phone screen specifically
        is_phone, phone_confidence, phone_reason = LivenessDetector.detect_phone_screen(image_array)
        
        if is_phone:
            return is_phone, phone_confidence, phone_reason
        
        # Additional checks for other screen types
        try:
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            else:
                image_bgr = image_array
                
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            
            # Check for uniform brightness patterns common in screens
            brightness_variance = np.var(gray)
            if brightness_variance < 500:  # Very uniform suggests screen
                logger.warning(f"Screen-like uniform brightness detected: variance={brightness_variance:.2f}")
                return True, 0.7, "La imagen muestra patrones uniformes característicos de pantalla"
            
            return False, 0.3, None
            
        except Exception as e:
            logger.error(f"Error in screen attack detection: {e}", exc_info=True)
            return False, 0.3, None

    @staticmethod
    def check_liveness(
        image_array: np.ndarray,
        min_liveness_score: Optional[float] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Comprehensive liveness check combining all anti-spoofing methods.
        
        Args:
            image_array: Image as numpy array in RGB format
            min_liveness_score: Minimum score to pass (uses config default if None)
            
        Returns:
            Tuple of (is_live: bool, error_message: Optional[str])
        """
        if min_liveness_score is None:
            min_liveness_score = settings.ANTI_SPOOFING_MIN_LIVENESS_SCORE
        
        if not settings.ANTI_SPOOFING_ENABLED:
            logger.debug("Anti-spoofing is disabled")
            return True, None
        
        # Check for photo attack
        is_photo, photo_confidence, photo_reason = LivenessDetector.detect_photo_attack(image_array)
        if is_photo and photo_confidence >= min_liveness_score:
            return False, ERROR_PHOTO_ATTACK_DETECTED
        
        # Check for phone screen
        is_phone, phone_confidence, phone_reason = LivenessDetector.detect_phone_screen(image_array)
        if is_phone and phone_confidence >= min_liveness_score:
            return False, ERROR_PHONE_SCREEN_DETECTED
        
        # Check for general screen attack
        is_screen, screen_confidence, screen_reason = LivenessDetector.detect_screen_attack(image_array)
        if is_screen and screen_confidence >= min_liveness_score:
            return False, ERROR_SCREEN_ATTACK_DETECTED
        
        logger.debug("Liveness check passed")
        return True, None

    @staticmethod
    def _analyze_texture_variation(gray: np.ndarray) -> float:
        """
        Analyze texture variation using Local Binary Pattern (LBP).
        
        Real faces have more texture variation than printed photos.
        
        Args:
            gray: Grayscale image array
            
        Returns:
            Texture variation score (0.0-1.0, higher = more variation)
        """
        try:
            # Use Laplacian to measure texture variation
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()
            
            # Normalize considering image resolution
            # Lower resolution images naturally have less variation
            height, width = gray.shape
            image_resolution = height * width
            
            # Adjust normalization factor based on resolution
            # Base factor for 640x480, scale down for smaller images
            base_resolution = 640 * 480
            resolution_factor = image_resolution / base_resolution
            normalization_factor = 1000.0 * max(resolution_factor, 0.3)  # Minimum 0.3x
            
            normalized = min(variance / normalization_factor, 1.0)
            
            return float(normalized)
        except Exception as e:
            logger.debug(f"Error in texture variation analysis: {e}")
            return 0.5  # Default neutral score

    @staticmethod
    def _analyze_depth_variation(gray: np.ndarray) -> float:
        """
        Analyze depth variation using gradient analysis.
        
        Real faces have more depth gradients than flat photos.
        
        Args:
            gray: Grayscale image array
            
        Returns:
            Depth variation score (0.0-1.0, higher = more depth)
        """
        try:
            # Use Sobel operator to detect gradients (depth changes)
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            
            # Calculate variance of gradient magnitude
            gradient_variance = gradient_magnitude.var()
            
            # Normalize considering image resolution
            height, width = gray.shape
            image_resolution = height * width
            
            # Adjust normalization factor based on resolution
            base_resolution = 640 * 480
            resolution_factor = image_resolution / base_resolution
            normalization_factor = 5000.0 * max(resolution_factor, 0.3)  # Minimum 0.3x
            
            normalized = min(gradient_variance / normalization_factor, 1.0)
            
            return float(normalized)
        except Exception as e:
            logger.debug(f"Error in depth variation analysis: {e}")
            return 0.5

    @staticmethod
    def _analyze_edge_patterns(gray: np.ndarray) -> float:
        """
        Analyze edge patterns for photo characteristics.
        
        Args:
            gray: Grayscale image array
            
        Returns:
            Edge pattern score (0.0-1.0)
        """
        try:
            # Use Canny edge detection
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # Real faces typically have moderate edge density
            # Very high or very low suggests photo
            if edge_density < 0.05:  # Too few edges
                return 0.3
            elif edge_density > 0.3:  # Too many edges (may indicate compression artifacts)
                return 0.6
            
            return 0.8  # Normal edge density
        except Exception as e:
            logger.debug(f"Error in edge pattern analysis: {e}")
            return 0.5

    @staticmethod
    def _detect_rectangular_borders(gray: np.ndarray) -> bool:
        """
        Detect perfect rectangular borders that may indicate device edges.
        
        Args:
            gray: Grayscale image array
            
        Returns:
            True if perfect rectangular borders are detected
        """
        try:
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return False
            
            # Check if any contour is a perfect rectangle
            height, width = gray.shape
            image_area = height * width
            
            for contour in contours:
                # Approximate contour
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Check if it's a rectangle (4 corners)
                if len(approx) == 4:
                    # Check if it's near the image borders (device edge)
                    rect = cv2.boundingRect(contour)
                    x, y, w, h = rect
                    
                    # Check if rectangle is near edges and covers significant area
                    near_edge = (
                        x < width * 0.1 or (x + w) > width * 0.9 or
                        y < height * 0.1 or (y + h) > height * 0.9
                    )
                    area_ratio = (w * h) / image_area
                    
                    if near_edge and area_ratio > 0.3:
                        return True
            
            return False
        except Exception as e:
            logger.debug(f"Error in rectangular border detection: {e}")
            return False

    @staticmethod
    def _analyze_reflection_patterns(gray: np.ndarray) -> float:
        """
        Analyze reflection patterns. Screens have characteristic reflections.
        
        Args:
            gray: Grayscale image array
            
        Returns:
            Reflection variation score (0.0-1.0, lower = more screen-like)
        """
        try:
            # Analyze brightness variation
            # Screens often have more uniform reflections
            brightness_std = np.std(gray)
            
            # Normalize (typical range: 0-100)
            normalized = min(brightness_std / 50.0, 1.0)
            
            return float(normalized)
        except Exception as e:
            logger.debug(f"Error in reflection pattern analysis: {e}")
            return 0.5

    @staticmethod
    def _analyze_pixel_grid_patterns(gray: np.ndarray) -> float:
        """
        Analyze pixel grid patterns from screen subpixels.
        
        Args:
            gray: Grayscale image array
            
        Returns:
            Grid pattern score (0.0-1.0, higher = more grid-like)
        """
        try:
            # Use Fourier Transform to detect periodic patterns
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.abs(f_shift)
            
            # Check for strong periodic patterns (indicates pixel grid)
            # Look for peaks in frequency domain
            height, width = gray.shape
            center_y, center_x = height // 2, width // 2
            
            # Check surrounding area for strong patterns
            pattern_strength = np.mean(magnitude_spectrum[center_y-20:center_y+20, 
                                                          center_x-20:center_x+20])
            
            # Normalize
            normalized = min(pattern_strength / 10000.0, 1.0)
            
            return float(normalized)
        except Exception as e:
            logger.debug(f"Error in pixel grid pattern analysis: {e}")
            return 0.3  # Default to not detecting grid

    @staticmethod
    def _analyze_brightness_patterns(gray: np.ndarray) -> float:
        """
        Analyze brightness patterns characteristic of screens.
        
        Args:
            gray: Grayscale image array
            
        Returns:
            Brightness pattern score (0.0-1.0, higher = more screen-like)
        """
        try:
            # Screens often have more uniform brightness with specific patterns
            # Check for very uniform brightness
            brightness_variance = np.var(gray)
            
            # Very low variance suggests screen
            if brightness_variance < 500:
                return 0.8
            
            # Check for block-like patterns (compression artifacts in photos)
            # This is less reliable, so lower weight
            return 0.3
        except Exception as e:
            logger.debug(f"Error in brightness pattern analysis: {e}")
            return 0.3

