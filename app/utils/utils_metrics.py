from app.supabase import supabase
from app.schemas.schemas import MetricsRequest
from app.config import settings
import logging
import httpx

# Set up logger for this module
logger = logging.getLogger(__name__)

def get_metrics_from_supabase():
    """Get metrics from supabase"""
    # metrics = supabase.table("metrics").select("*").execute()
    return []

async def fetch_run_data_from_happyrobot(run_id: str, organization_id: str):
    """Fetch run data from HappyRobot API asynchronously"""
    try:
        if not settings.happyrobot_bearer_token:
            logger.warning("HappyRobot bearer token not configured, skipping API call")
            return None, None
        
        url = f"{settings.happyrobot_api_base_url}/runs/{run_id}"
        headers = {
            "authorization": f"Bearer {settings.happyrobot_bearer_token}",
            "x-organization-id": organization_id
        }
        
        logger.info(f"Fetching run data from HappyRobot API: {url}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            duration = data.get("duration")
            status = data.get("status")
            
            logger.info(f"Successfully fetched run data - duration: {duration}, status: {status}")
            return duration, status
        
    except httpx.TimeoutException:
        logger.error("Timeout fetching run data from HappyRobot API")
        return None, None
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching run data from HappyRobot API: {str(e)}")
        return None, None
    except Exception as e:
        logger.error(f"Unexpected error fetching run data: {str(e)}")
        return None, None


async def store_metrics_in_supabase(metrics: MetricsRequest):
    """Store metrics in supabase with calculated fields"""
    logger.info(f"Storing metrics: {metrics}")
    
    # Convert Pydantic model to dictionary
    metrics_dict = metrics.model_dump()
    
    # Fetch duration and status from HappyRobot API (await the async call)
    duration, status = await fetch_run_data_from_happyrobot(metrics.run_id, metrics.organization_id)
    metrics_dict['call_duration'] = duration
    metrics_dict['call_status'] = status
    
    # Calculate negotiation_performance: difference between carrier's initial offer and agreed rate
    # Positive value means we negotiated down from carrier's offer
    negotiation_performance = None
    if metrics.carrier_initial_offer is not None and metrics.load_agreed_rate is not None:
        negotiation_performance = float(metrics.carrier_initial_offer) - float(metrics.load_agreed_rate)
        logger.info(f"Calculated negotiation_performance: {negotiation_performance}")
    
    # Calculate rate_difference: difference between agreed rate and loadboard rate
    # Positive value means we got more than the loadboard rate
    rate_difference = None
    if metrics.load_loadboard_rate is not None and metrics.load_agreed_rate is not None:
        rate_difference = float(metrics.load_agreed_rate) - float(metrics.load_loadboard_rate)
        logger.info(f"Calculated rate_difference: {rate_difference}")
    
    # Add calculated fields to the metrics dictionary
    metrics_dict['negotiation_performance'] = negotiation_performance
    metrics_dict['rate_difference'] = rate_difference
    
    logger.debug(f"Final metrics to store: {metrics_dict}")
    
    # Insert into Supabase
    try:
        result = supabase.table("metrics").insert(metrics_dict).execute()
        logger.info(f"Successfully stored metrics in Supabase")
        return True
    except Exception as e:
        logger.error(f"Error storing metrics in Supabase: {str(e)}")
        raise e