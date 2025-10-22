from fastapi import APIRouter, Depends, Query, HTTPException
from app.schemas.schemas import LoadsResponse, LoadResponse
from app.utils.utils_loads import find_loads_within_radius, process_parameters
from app.auth import verify_api_key
from typing import Optional
import logging
import time

# Set up logger for this module
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/loads", tags=["loads"])

@router.get("/find_matching_loads", response_model=LoadsResponse)
async def find_matching_loads(
    equipment_type: str = Query(..., description="Type of equipment needed (required)"),
    origin: str = Query(..., description="Starting location (required)"),
    destination: Optional[str] = Query(None, description="Delivery location (optional)"),
    pickup_datetime: Optional[str] = Query(None, description="Date and time for pickup (optional)"),
    api_key: str = Depends(verify_api_key)
):
    """
    Find matching loads based on the given parameters
    
    Args:
        equipment_type: Type of equipment needed (required)
        origin: Starting location (required)
        destination: Delivery location (optional)
        pickup_datetime: Date and time for pickup (optional)
        api_key: API key for authentication (validated via dependency)
    
    Returns:
        LoadsResponse: Response with the matching loads
    """
    start_time = time.time()
    logger.info(f"Starting load search - Equipment: {equipment_type}, Origin: {origin}")
    logger.debug(f"API key provided: {api_key[:8]}...")
    logger.debug(f"Optional parameters - Destination: {destination}, Pickup: {pickup_datetime}")
    
    try:
        # API key is automatically validated by the dependency
        logger.debug("API key validation passed")
        # process parameters
        equipment_type, pickup_datetime = process_parameters(equipment_type, pickup_datetime)

        # Find matching loads
        logger.debug(f"Calling find_loads_within_radius with: {equipment_type}, {origin}, {destination}, {pickup_datetime}")
        raw_loads_data, omitted_parameters = find_loads_within_radius(equipment_type, origin, destination, pickup_datetime)
        logger.debug(f"Found {len(raw_loads_data)} matching loads; omitted_parameters={omitted_parameters}")
        
        # Convert raw database data to LoadResponse models
        matching_loads = [LoadResponse(**load_data) for load_data in raw_loads_data]

        loads_available = len(matching_loads) > 0
        message = f"Number of available loads: {len(matching_loads)}"
        
        if loads_available:
            logger.info(f"Load search successful - Found {len(matching_loads)} loads for {equipment_type} from {origin}")
        else:
            logger.info(f"Load search completed - No loads found for {equipment_type} from {origin}")
        
        processing_time = time.time() - start_time
        logger.info(f"Load search completed in {processing_time:.3f}s")
        
        return LoadsResponse(
            statusCode=200,
            loads_available=loads_available,
            message=message,
            loads=matching_loads,
            omitted_parameters=omitted_parameters
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error during load search for {equipment_type} from {origin}: {str(e)}")
        logger.error(f"Processing time: {processing_time:.3f}s")
        raise HTTPException(status_code=500, detail="Internal server error during load search")