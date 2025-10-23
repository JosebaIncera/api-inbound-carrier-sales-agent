from fastapi import APIRouter, Depends, Query, HTTPException
from app.schemas.schemas import LoadsResponse, LoadResponse
from app.utils.utils_loads import find_loads_within_radius, process_parameters
from app.auth import verify_api_key
from typing import Optional
import logging
import time


# Set up logger for this module
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/get_metrics", response_model=MetricsResponse)
async def get_metrics(api_key: str = Depends(verify_api_key)):
    """Get metrics endpoint with API key validation"""
    start_time = time.time()
    logger.info("Get metrics endpoint called")
    try:
        logger.debug("API key validation passed")
        logger.debug("Returning metrics")

        # get metrics from supabase
        metrics = get_metrics_from_supabase()
        logger.debug(f"Metrics: {metrics}")
        
        # return metrics
        return MetricsResponse(
            statusCode=200,
            metrics=metrics
        )
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error in get_metrics endpoint: {str(e)}")
        logger.error(f"Processing time: {processing_time:.3f}s")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/store_metrics", response_model=MetricsResponse)
async def store_metrics(metrics: MetricsRequest, api_key: str = Depends(verify_api_key)):
    """Store metrics endpoint with API key validation"""
    start_time = time.time()
    logger.info("Store metrics endpoint called")
    try:
        logger.debug("API key validation passed")
        logger.debug("Storing metrics")

        # store metrics in supabase
        success = store_metrics_in_supabase(metrics)
        if success:
            message = "Metrics stored successfully"
        else:
            message = "Failed to store metrics"
        
        # return metrics
        return MetricsResponse(statusCode=200, success=success, message=message)
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error in store_metrics endpoint: {str(e)}")
        logger.error(f"Processing time: {processing_time:.3f}s")
        raise HTTPException(status_code=500, detail="Internal server error")