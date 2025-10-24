from fastapi import APIRouter, Depends, Query, HTTPException
from app.schemas.schemas import CarrierResponse
from app.utils.utils_carriers import validate_mc_format, extract_mc_digits, check_carrier_exists
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
    
    try:
        # API key is automatically validated by the dependency
        logger.debug("API key validation passed")
        
        # Validar formato del MC number
        logger.debug(f"Calling validate_mc_format for: {mc_number}")
        format_valid = validate_mc_format(mc_number)
        logger.debug(f"MC format validation result: {format_valid}")
        
        if not format_valid:
            message = f"MC number {mc_number} is invalid. Expected format: MC XXXXXX"
            logger.warning(f"MC validation failed: {mc_number} - Invalid format")
            processing_time = time.time() - start_time
            logger.info(f"MC validation completed in {processing_time:.3f}s for: {mc_number}")
            
            return CarrierResponse(
                statusCode=200,
                verified_carrier=False,
                message=message
            )
        
        # Extraer los dígitos del MC number
        logger.debug(f"Extracting MC digits from: {mc_number}")
        mc_digits = extract_mc_digits(mc_number)
        logger.debug(f"Extracted MC digits: {mc_digits}")
        
        if not mc_digits:
            message = f"Could not extract MC digits from: {mc_number}"
            logger.error(f"MC digit extraction failed: {mc_number}")
            processing_time = time.time() - start_time
            logger.info(f"MC validation completed in {processing_time:.3f}s for: {mc_number}")
            
            return CarrierResponse(
                statusCode=200,
                verified_carrier=False,
                message=message
            )
        
        # Verificar si el carrier existe en la base de datos
        logger.debug(f"Checking if carrier exists with MC digits: {mc_digits}")
        carrier_exists = check_carrier_exists(mc_digits)
        logger.debug(f"Carrier exists check result: {carrier_exists}")
        
        if carrier_exists:
            message = f"MC number {mc_number} is valid and carrier exists in database"
            logger.info(f"MC validation successful: {mc_number} - Carrier found in database")
        else:
            message = f"MC number {mc_number} has valid format but carrier not found in database"
            logger.warning(f"MC validation failed: {mc_number} - Carrier not found in database")
        
        processing_time = time.time() - start_time
        logger.info(f"MC validation completed in {processing_time:.3f}s for: {mc_number}")
        
        return CarrierResponse(
            statusCode=200,
            verified_carrier=carrier_exists,
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
