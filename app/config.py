import os
from typing import Optional
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

class Settings:
    """Application settings and configuration"""
    
    def __init__(self):
        # API Key - can be set via environment variable or use default for development
        self.api_key: str = os.getenv("API_KEY", "test-api-key-12345")
        logger.debug(f"API key loaded: {self.api_key[:8]}...")
        
        # Database settings
        self.database_url: Optional[str] = os.getenv("DATABASE_URL")
        if self.database_url:
            logger.debug("Database URL configured")
        else:
            logger.debug("No database URL configured")
        
        # Other settings can be added here
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        logger.debug(f"Debug mode: {self.debug}")
        
        logger.info("Settings initialized successfully")
    
    def validate_api_key(self, provided_key: str) -> bool:
        """Validate the provided API key"""
        logger.debug(f"Validating API key: {provided_key[:8]}...")
        is_valid = provided_key == self.api_key
        logger.debug(f"API key validation result: {is_valid}")
        return is_valid

# Global settings instance
settings = Settings()
