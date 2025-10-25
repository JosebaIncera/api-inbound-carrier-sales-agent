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

            status = data.get("status")
            duration = ""
            events = data.get("events", [])
            for event in events:
                if event.get("type") == "session":
                    duration = event.get("duration")
                    break
            
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

async def update_metrics_in_supabase():
    """Update metrics in supabase by fetching rows where call_status is 'running' and updating them with HappyRobot data"""
    logger.info("Starting metrics update process")
    
    try:
        # Fetch rows from the metrics table where call_status is "running"
        result = supabase.table("metrics").select("id, organization_id, run_id").eq("call_status", "running").execute()
        
        if not result.data:
            logger.info("No metrics found to update")
            return {"updated_count": 0, "message": "No metrics found to update"}
        
        logger.info(f"Found {len(result.data)} metrics to update")
        
        updated_count = 0
        failed_count = 0
        
        # Process each row
        for row in result.data:
            row_id = row.get("id")
            organization_id = row.get("organization_id")
            run_id = row.get("run_id")
            
            logger.info(f"Processing metric row {row_id} for run_id: {run_id}, organization_id: {organization_id}")
            
            # Fetch run data from HappyRobot API
            duration, status = await fetch_run_data_from_happyrobot(run_id, organization_id)
            
            # Update the row in the metrics table
            update_data = {
                "call_duration": duration,
                "call_status": status
            }
            
            try:
                supabase.table("metrics").update(update_data).eq("id", row_id).execute()
                logger.info(f"Successfully updated metric row {row_id} with duration: {duration}, status: {status}")
                updated_count += 1
            except Exception as e:
                logger.error(f"Error updating metric row {row_id}: {str(e)}")
                failed_count += 1
        
        logger.info(f"Metrics update complete. Updated: {updated_count}, Failed: {failed_count}")
        return {
            "updated_count": updated_count,
            "failed_count": failed_count,
            "message": f"Successfully updated {updated_count} metrics"
        }
        
    except Exception as e:
        logger.error(f"Error in update_metrics_in_supabase: {str(e)}")
        raise e