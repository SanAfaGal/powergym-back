"""
Application-wide constants for PowerGym API.

This module centralizes all constant values used throughout the application
to ensure consistency and easy maintenance.
"""

from typing import Final

# ============================================================================
# API Constants
# ============================================================================

API_V1_PREFIX: Final[str] = "/api/v1"
API_TITLE: Final[str] = "PowerGym API"
API_VERSION: Final[str] = "1.0.0"

# ============================================================================
# Pagination Constants
# ============================================================================

DEFAULT_PAGE_SIZE: Final[int] = 100
MAX_PAGE_SIZE: Final[int] = 500
MIN_PAGE_SIZE: Final[int] = 1
DEFAULT_OFFSET: Final[int] = 0

# ============================================================================
# Search Constants
# ============================================================================

DEFAULT_SEARCH_LIMIT: Final[int] = 50
MAX_SEARCH_LIMIT: Final[int] = 200

# ============================================================================
# Face Recognition Constants
# ============================================================================

DEFAULT_FACE_RECOGNITION_TOLERANCE: Final[float] = 0.6
MIN_FACE_RECOGNITION_TOLERANCE: Final[float] = 0.0
MAX_FACE_RECOGNITION_TOLERANCE: Final[float] = 1.0
DEFAULT_EMBEDDING_DIMENSIONS: Final[int] = 512
DEFAULT_INSIGHTFACE_DET_SIZE: Final[int] = 640
DEFAULT_INSIGHTFACE_CTX_ID: Final[int] = -1  # CPU
DEFAULT_INSIGHTFACE_MODEL: Final[str] = "buffalo_s"

# ============================================================================
# Image Processing Constants
# ============================================================================

DEFAULT_MAX_IMAGE_SIZE_MB: Final[int] = 5
DEFAULT_IMAGE_COMPRESSION_QUALITY: Final[int] = 85
DEFAULT_THUMBNAIL_COMPRESSION_QUALITY: Final[int] = 70
DEFAULT_THUMBNAIL_WIDTH: Final[int] = 150
DEFAULT_THUMBNAIL_HEIGHT: Final[int] = 150
DEFAULT_EMBEDDING_COMPRESSION_LEVEL: Final[int] = 9
ALLOWED_IMAGE_FORMATS: Final[list[str]] = ["jpg", "jpeg", "png", "webp"]

# ============================================================================
# Rate Limiting Constants
# ============================================================================

DEFAULT_RATE_LIMIT_PER_MINUTE: Final[int] = 60
DEVELOPMENT_RATE_LIMIT_PER_MINUTE: Final[int] = 120

# ============================================================================
# Database Constants
# ============================================================================

DEFAULT_DB_POOL_SIZE: Final[int] = 5
DEFAULT_DB_MAX_OVERFLOW: Final[int] = 10

# ============================================================================
# Time Constants
# ============================================================================

SECONDS_PER_MINUTE: Final[int] = 60
MINUTES_PER_HOUR: Final[int] = 60
HOURS_PER_DAY: Final[int] = 24
DAYS_PER_WEEK: Final[int] = 7

# ============================================================================
# Reward Constants
# ============================================================================

REWARD_ELIGIBILITY_ATTENDANCE_THRESHOLD: Final[int] = 20
REWARD_EXPIRATION_DAYS: Final[int] = 7

# ============================================================================
# Error Messages
# ============================================================================

ERROR_CLIENT_NOT_FOUND: Final[str] = "Client not found"
ERROR_SUBSCRIPTION_NOT_FOUND: Final[str] = "Subscription not found"
ERROR_PLAN_NOT_FOUND: Final[str] = "Plan not found"
ERROR_USER_NOT_FOUND: Final[str] = "User not found"
ERROR_PRODUCT_NOT_FOUND: Final[str] = "Product not found"
ERROR_DNI_ALREADY_EXISTS: Final[str] = "A client with this DNI number already exists"
ERROR_INVALID_CREDENTIALS: Final[str] = "Could not validate credentials"
ERROR_INSUFFICIENT_PERMISSIONS: Final[str] = "Not enough permissions"
ERROR_INTERNAL_SERVER: Final[str] = "Internal server error"

# ============================================================================
# Success Messages
# ============================================================================

SUCCESS_CLIENT_CREATED: Final[str] = "Client created successfully"
SUCCESS_CLIENT_UPDATED: Final[str] = "Client updated successfully"
SUCCESS_CLIENT_DELETED: Final[str] = "Client deleted successfully"
SUCCESS_SUBSCRIPTION_CREATED: Final[str] = "Subscription created successfully"

