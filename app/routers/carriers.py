from fastapi import APIRouter, Depends, Query, HTTPException
from app.schemas.schemas import CarrierResponse
from app.utils.utils_carriers import validate_mc_format
from app.auth import verify_api_key
import logging
import time

# Set up logger for this module
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/carriers", tags=["carriers"])

@router.get("/validate_carrier", response_model=CarrierResponse)
async def validate_carrier(
    mc_number: str = Query(..., description="MC number to validate (format: MC XXXXXX)"),
    api_key: str = Depends(verify_api_key)
):
    """
    Valida si un número MC sigue el formato correcto 'MC XXXXXX'
    
    Args:
        mc_number: Número MC a validar (formato completo: MC XXXXXX)
        api_key: API key válida para autenticación (validated via dependency)
    
    Returns:
        CarrierResponse: Respuesta con el resultado de la validación
    """
    start_time = time.time()
    logger.info(f"Starting MC validation for: {mc_number}")
    logger.debug(f"API key provided: {api_key[:8]}...")
    
    try:
        # API key is automatically validated by the dependency
        logger.debug("API key validation passed")
        
        # Validar directamente el MC number proporcionado
        logger.debug(f"Calling validate_mc_format for: {mc_number}")
        is_valid = validate_mc_format(mc_number)
        logger.debug(f"MC validation result: {is_valid}")
        
        if is_valid:
            message = f"MC number {mc_number} is valid"
            logger.info(f"MC validation successful: {mc_number}")
        else:
            message = f"MC number {mc_number} is invalid. Expected format: MC XXXXXX"
            logger.warning(f"MC validation failed: {mc_number} - Invalid format")
        
        processing_time = time.time() - start_time
        logger.info(f"MC validation completed in {processing_time:.3f}s for: {mc_number}")
        
        return CarrierResponse(
            statusCode=200,
            verified_carrier=is_valid,
            message=message
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error during MC validation for {mc_number}: {str(e)}")
        logger.error(f"Processing time: {processing_time:.3f}s")
        raise HTTPException(status_code=500, detail="Internal server error during MC validation")

@router.get("/health")
async def health_check():
    """Endpoint de health check"""
    logger.info("Carriers health check requested")
    logger.debug("Returning carriers health status")
    return {"status": "healthy", "service": "Carrier Sales API"}

@router.get("/carriers")
async def get_carriers(api_key: str = Depends(verify_api_key)):
    """Get carriers endpoint with API key validation"""
    start_time = time.time()
    logger.info("Get carriers endpoint called")
    logger.debug(f"API key provided: {api_key[:8]}...")
    
    try:
        logger.debug("API key validation passed")
        logger.debug("Returning carriers list")
        
        processing_time = time.time() - start_time
        logger.info(f"Get carriers completed in {processing_time:.3f}s")
        
        return {"message": "Hello, World!"}
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error in get_carriers endpoint: {str(e)}")
        logger.error(f"Processing time: {processing_time:.3f}s")
        raise HTTPException(status_code=500, detail="Internal server error")
