"""
Application configuration settings.

This module defines all application settings using Pydantic BaseSettings,
which automatically loads values from environment variables or .env files.
"""

import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    PowerGym Backend Configuration Settings.
    
    This class manages all application settings loaded from environment variables
    or .env files. Settings are validated using Pydantic and provide type hints
    for better IDE support and runtime validation.
    """

    # ==================== APP CONFIG ====================
    PROJECT_NAME: str = "PowerGym API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # ==================== SECURITY ====================
    SECRET_KEY: str = Field(..., description="JWT secret key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=300,
        description="Access token expiration time in minutes (default: 5 hours)"
    )
    REFRESH_TOKEN_EXPIRE_HOURS: int = Field(
        default=12,
        description="Refresh token expiration time in hours (default: 12 hours, maximum session)"
    )
    BIOMETRIC_ENCRYPTION_KEY: str = Field(..., description="Encryption key for biometric data")

    # ==================== CORS & ALLOWED ORIGINS ====================
    # Store as string to avoid JSON parsing issues, convert to list in property
    ALLOWED_ORIGINS_STR: str = Field(
        default="http://localhost:5173",
        description="Allowed origins for CORS (comma-separated string)"
    )
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """
        Parse ALLOWED_ORIGINS from comma-separated string to list.
        
        Returns:
            List of allowed origin URLs for CORS
        """
        if not self.ALLOWED_ORIGINS_STR or self.ALLOWED_ORIGINS_STR.strip() == ',':
            return ["http://localhost:5173"]
        origins = [origin.strip() for origin in self.ALLOWED_ORIGINS_STR.split(',') if origin.strip()]
        return origins if origins else ["http://localhost:5173"]

    # ==================== SUPER ADMIN ====================
    SUPER_ADMIN_USERNAME: str = Field(..., description="Initial admin username")
    SUPER_ADMIN_PASSWORD: str = Field(..., description="Initial admin password")
    SUPER_ADMIN_EMAIL: str = Field(..., description="Initial admin email")
    SUPER_ADMIN_FULL_NAME: str = Field(..., description="Initial admin full name")

    # ==================== DATABASE ====================
    DATABASE_URL: str = Field(..., description="Database URL")

    POSTGRES_USER: Optional[str] = Field(None, description="PostgreSQL username")
    POSTGRES_PASSWORD: Optional[str] = Field(None, description="PostgreSQL password")
    POSTGRES_DB: Optional[str] = Field(None, description="PostgreSQL database name")
    POSTGRES_HOST: Optional[str] = Field(None, description="PostgreSQL host")
    POSTGRES_PORT: Optional[int] = Field(None, description="PostgreSQL port")

    # ==================== FACE RECOGNITION ====================
    EMBEDDING_DIMENSIONS: int = Field(..., description="Face embedding dimensions (typically 512 for InsightFace)")

    # InsightFace Configuration
    INSIGHTFACE_MODEL: str = Field(
        default="buffalo_s",
        description="InsightFace model name (buffalo_s, buffalo_l, etc.)"
    )
    INSIGHTFACE_DET_SIZE: int = Field(
        default=640,
        gt=0,
        description="InsightFace detection size in pixels"
    )
    INSIGHTFACE_CTX_ID: int = Field(
        default=-1,
        description="InsightFace context ID (-1 for CPU, 0+ for GPU)"
    )

    FACE_RECOGNITION_TOLERANCE: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Tolerance for face recognition similarity threshold (0.0-1.0)"
    )

    # ==================== IMAGE PROCESSING ====================
    MAX_IMAGE_SIZE_MB: int = Field(
        default=5,
        gt=0,
        description="Maximum image size in MB"
    )
    ALLOWED_IMAGE_FORMATS_STR: str = Field(
        default="jpg,jpeg,png,webp",
        description="Allowed image formats (comma-separated string)"
    )
    
    @property
    def ALLOWED_IMAGE_FORMATS(self) -> List[str]:
        """
        Parse ALLOWED_IMAGE_FORMATS from comma-separated string to list.
        
        Returns:
            List of allowed image format extensions (lowercase)
        """
        if not self.ALLOWED_IMAGE_FORMATS_STR or self.ALLOWED_IMAGE_FORMATS_STR.strip() == ',':
            return ["jpg", "jpeg", "png", "webp"]
        formats = [fmt.strip().lower() for fmt in self.ALLOWED_IMAGE_FORMATS_STR.split(',') if fmt.strip()]
        return formats if formats else ["jpg", "jpeg", "png", "webp"]
    IMAGE_COMPRESSION_QUALITY: int = Field(
        default=85,
        ge=1,
        le=100,
        description="Image compression quality (1-100)"
    )
    THUMBNAIL_COMPRESSION_QUALITY: int = Field(
        default=70,
        ge=1,
        le=100,
        description="Thumbnail compression quality (1-100)"
    )
    THUMBNAIL_WIDTH: int = Field(default=150, gt=0, description="Thumbnail width in pixels")
    THUMBNAIL_HEIGHT: int = Field(default=150, gt=0, description="Thumbnail height in pixels")
    EMBEDDING_COMPRESSION_LEVEL: int = Field(
        default=9,
        ge=0,
        le=9,
        description="Embedding compression level (0-9)"
    )
    ENABLE_COMPRESSION: bool = Field(default=True, description="Enable image compression")

    # ==================== RATE LIMITING ====================
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        gt=0,
        description="Rate limit requests per minute"
    )

    # ==================== ADMIN UI ====================
    ADMINER_PORT: Optional[int] = Field(None, description="Adminer UI port")

    # ==================== TELEGRAM NOTIFICATIONS ====================
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(None, description="Telegram bot token")
    TELEGRAM_CHAT_ID: Optional[str] = Field(None, description="Telegram chat ID for notifications")
    TELEGRAM_ENABLED: bool = Field(default=True, description="Enable Telegram notifications")

    # ==================== REWARDS CONFIGURATION ====================
    REWARD_ATTENDANCE_THRESHOLD: int = Field(
        default=20,
        gt=0,
        description="Minimum number of attendances required to qualify for a reward"
    )
    REWARD_DISCOUNT_PERCENTAGE: float = Field(
        default=20.0,
        ge=0.01,
        le=100.0,
        description="Default discount percentage for rewards (0.01 to 100.0)"
    )
    REWARD_EXPIRATION_DAYS: int = Field(
        default=7,
        gt=0,
        description="Number of days until a reward expires after becoming eligible"
    )
    REWARD_ELIGIBLE_PLAN_UNITS_STR: str = Field(
        default="month",
        description="Comma-separated list of plan duration units eligible for rewards (e.g., 'month,week')"
    )

    @property
    def REWARD_ELIGIBLE_PLAN_UNITS(self) -> List[str]:
        """
        Parse REWARD_ELIGIBLE_PLAN_UNITS from comma-separated string to list.
        
        Returns:
            List of eligible plan duration units (e.g., ['month', 'week'])
        """
        if not self.REWARD_ELIGIBLE_PLAN_UNITS_STR or self.REWARD_ELIGIBLE_PLAN_UNITS_STR.strip() == ',':
            return ["month"]
        units = [unit.strip().lower() for unit in self.REWARD_ELIGIBLE_PLAN_UNITS_STR.split(',') if unit.strip()]
        return units if units else ["month"]

    class Config:
        """
        Pydantic configuration for Settings.
        
        Environment file loading priority:
        1. ENV_FILE environment variable (if set)
        2. .env file (if exists)
        3. .env.{ENVIRONMENT} file (if exists)
        
        Note: .env takes priority over .env.{ENVIRONMENT} to allow manual override.
        """
        env_file = os.getenv(
            "ENV_FILE",
            ".env" if os.path.exists(".env") 
            else (f".env.{os.getenv('ENVIRONMENT', 'development')}"
                  if os.path.exists(f".env.{os.getenv('ENVIRONMENT', 'development')}")
                  else None)
        )
        case_sensitive = True
        extra = "ignore"  # Ignore undefined environment variables


settings = Settings()