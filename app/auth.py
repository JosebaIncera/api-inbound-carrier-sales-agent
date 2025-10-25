from fastapi import Depends, HTTPException, Header
from typing import Optional
from app.config import settings
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="x-api-key")) -> str:
    """
    Dependency function to verify API key on every endpoint.
    
    This function will be called automatically by FastAPI for any endpoint
    that includes it as a dependency.
    
    Args:
        x_api_key: API key from the x-api-key header
        
    Returns:
        str: The validated API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    logger.debug("Starting API key verification")
    
    if not x_api_key:
        logger.warning("API key verification failed - No API key provided")
        logger.debug("Raising HTTPException for missing API key")
        raise HTTPException(
            status_code=401,
            detail="API key is required. Please provide it in the 'x-api-key' header."
        )
    
    logger.debug(f"API key provided: {x_api_key[:8]}...")
    
    if not settings.validate_api_key(x_api_key):
        logger.warning(f"API key verification failed - Invalid API key: {x_api_key[:8]}...")
        logger.debug("Raising HTTPException for invalid API key")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    logger.debug("API key verification successful")
    return x_api_key

# Alternative: Optional API key validation (for endpoints that don't require auth)
async def verify_api_key_optional(x_api_key: Optional[str] = Header(None, alias="x-api-key")) -> Optional[str]:
    """
    Optional API key verification for endpoints that can work with or without authentication.
    
    Args:
        x_api_key: API key from the x-api-key header
        
    Returns:
        Optional[str]: The validated API key if provided, None otherwise
        
    Raises:
        HTTPException: If API key is provided but invalid
    """
    logger.debug("Starting optional API key verification")
    
    if not x_api_key:
        logger.debug("No API key provided - proceeding without authentication")
        return None
    
    logger.debug(f"API key provided: {x_api_key[:8]}...")
    
    if not settings.validate_api_key(x_api_key):
        logger.warning(f"Optional API key verification failed - Invalid API key: {x_api_key[:8]}...")
        logger.debug("Raising HTTPException for invalid API key")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    logger.debug("Optional API key verification successful")
    return x_api_key
