from geopy.geocoders import Nominatim
import geopy.geocoders
from math import radians, cos
from app.supabase import supabase
from datetime import datetime

import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

geopy.geocoders.options.default_timeout = 3
geolocator = Nominatim(user_agent="load-matcher")
logger.debug("Initialized Nominatim geolocator for load matching")

def get_coordinates(city: str, state: str | None = None):
    """Get latitude and longitude coordinates for a city"""
    query = f"{city}, {state}" if state else city
    logger.debug(f"Getting coordinates for: {query}")
    
    try:
        location = geolocator.geocode(query)
        if location:
            logger.debug(f"Found coordinates for {query}: lat={location.latitude}, lng={location.longitude}")
            return location.latitude, location.longitude
        else:
            logger.warning(f"No coordinates found for: {query}")
            return None, None
            
    except Exception as e:
        logger.error(f"Error getting coordinates for {query}: {str(e)}")
        return None, None

def generate_query(equipment_type: str, origin_min_lat: float, origin_max_lat: float, origin_min_lng: float, origin_max_lng: float, destination_min_lat: float | None = None, destination_max_lat: float | None = None, destination_min_lng: float | None = None, destination_max_lng: float | None = None, pickup_datetime: datetime | None = None):
    """Generate a query based on the parameters"""
    # Determine what parameters are actually available
    has_destination = destination_min_lat is not None and destination_max_lat is not None and destination_min_lng is not None and destination_max_lng is not None
    # Defensive: treat empty-string-like pickup as absent
    if isinstance(pickup_datetime, str) and pickup_datetime.strip() == "":
        pickup_datetime = None
    has_pickup_datetime = pickup_datetime is not None
    logger.debug(f"Has Destination: {has_destination}, Has Pickup Datetime: {has_pickup_datetime}")
    # if only equipment_type, origin_lat and origin_lng are provided
    if has_destination and has_pickup_datetime:
        # All parameters
        query = (
            supabase.table("loads")
            .select("*")
            .eq("equipment_type", equipment_type)
            .gte("origin_lat", origin_min_lat)
            .lte("origin_lat", origin_max_lat)
            .gte("origin_lng", origin_min_lng)
            .lte("origin_lng", origin_max_lng)
            .gte("destination_lat", destination_min_lat)
            .lte("destination_lat", destination_max_lat)
            .gte("destination_lng", destination_min_lng)
            .lte("destination_lng", destination_max_lng)
            .eq("pickup_datetime", pickup_datetime)
            .limit(3)
        )
    elif has_destination and not has_pickup_datetime:
        # Equipment + Origin + Destination
        query = (
            supabase.table("loads")
            .select("*")
            .eq("equipment_type", equipment_type)
            .gte("origin_lat", origin_min_lat)
            .lte("origin_lat", origin_max_lat)
            .gte("origin_lng", origin_min_lng)
            .lte("origin_lng", origin_max_lng)
            .gte("destination_lat", destination_min_lat)
            .lte("destination_lat", destination_max_lat)
            .gte("destination_lng", destination_min_lng)
            .lte("destination_lng", destination_max_lng)
            .limit(3)
        )
    elif not has_destination and has_pickup_datetime:
        # Equipment + Origin + pickup_datetime
        query = (
            supabase.table("loads")
            .select("*")
            .eq("equipment_type", equipment_type)
            .gte("origin_lat", origin_min_lat)
            .lte("origin_lat", origin_max_lat)
            .gte("origin_lng", origin_min_lng)
            .lte("origin_lng", origin_max_lng)
            .eq("pickup_datetime", pickup_datetime)
            .limit(3)
        )
    else:
        # Equipment + Origin only
        query = (
            supabase.table("loads")
            .select("*")
            .eq("equipment_type", equipment_type)
            .gte("origin_lat", origin_min_lat)
            .lte("origin_lat", origin_max_lat)
            .gte("origin_lng", origin_min_lng)
            .lte("origin_lng", origin_max_lng)
            .limit(3)
        )
    logger.debug(f"Generated query: {query}")    
    return query

def get_bounding_box(lat: float, lng: float, radius: float) -> tuple[float, float, float, float]:
    """Get the bounding box for a given location and radius"""
    # Approximate bounding box around the coordinates
    # 1 degree ≈ 69 miles latitude
    lat_delta = radius / 69
    lng_delta = radius / (cos(radians(lat)) * 69)
    return lat - lat_delta, lat + lat_delta, lng - lng_delta, lng + lng_delta

def find_loads_within_radius(equipment_type: str, origin: str, destination: str | None = None, pickup_datetime: str | None = None):
    """Find loads within a specified radius of the origin location

    Returns a tuple: (loads_data, omitted_parameters)
    omitted_parameters lists which provided filters were dropped in the successful attempt.
    """
    logger.debug(f"Starting load search - Equipment: {equipment_type}, Origin: {origin}")
    logger.debug(f"Optional parameters - Destination: {destination}, Pickup: {pickup_datetime}")
    
    try:
        # Get coordinates for origin
        logger.debug(f"Getting coordinates for origin: {origin}")
        origin_lat, origin_lng = get_coordinates(origin)
        
        if not origin_lat or not origin_lng:
            logger.warning(f"Could not get coordinates for origin: {origin}")
            logger.debug("Returning empty loads list due to coordinate lookup failure")
            return [], []
        
        logger.debug(f"Origin coordinates: lat={origin_lat}, lng={origin_lng}")
        
        # Default radius in miles
        DEFAULT_RADIUS_MILES = 100  
        logger.debug(f"Using search radius: {DEFAULT_RADIUS_MILES} miles")
        
        # get origin bounding box
        origin_min_lat, origin_max_lat, origin_min_lng, origin_max_lng = get_bounding_box(origin_lat, origin_lng, DEFAULT_RADIUS_MILES)
        
        logger.debug(f"Search bounding box - Lat: {origin_min_lat:.4f} to {origin_max_lat:.4f}")
        logger.debug(f"Search bounding box - Lng: {origin_min_lng:.4f} to {origin_max_lng:.4f}")
        # ger coordinates for destination
        if destination:
            destination_lat, destination_lng = get_coordinates(destination)
            if not destination_lat or not destination_lng:
                logger.warning(f"Could not get coordinates for destination: {destination}")
                logger.debug("Returning empty loads list due to coordinate lookup failure")
                return [], []
            logger.debug(f"Destination coordinates: lat={destination_lat}, lng={destination_lng}")
            # get destination bounding box
            destination_min_lat, destination_max_lat, destination_min_lng, destination_max_lng = get_bounding_box(destination_lat, destination_lng, DEFAULT_RADIUS_MILES)
            logger.debug(f"Search bounding box - Lat: {destination_min_lat:.4f} to {destination_max_lat:.4f}")
            logger.debug(f"Search bounding box - Lng: {destination_min_lng:.4f} to {destination_max_lng:.4f}")
        else:
            destination_min_lat = None
            destination_max_lat = None
            destination_min_lng = None
            destination_max_lng = None

        logger.debug("Querying Supabase for matching loads")
        
        # Retry logic with progressive parameter removal
        # 1. Try with all parameters
        # 2. Try with equipment + origin + destination (without pickup_datetime)
        # 3. Try with equipment + origin only
        # Determine what parameters we actually have
        has_destination = destination_min_lat is not None and destination_max_lat is not None and destination_min_lng is not None and destination_max_lng is not None
        # Defensive: treat empty-string-like pickup as absent
        if isinstance(pickup_datetime, str) and pickup_datetime.strip() == "":
            pickup_datetime = None
        has_pickup_datetime = pickup_datetime is not None
        originally_provided_destination = has_destination
        originally_provided_pickup = has_pickup_datetime

        loads_data = []
        
        # Attempt 1: All available parameters
        logger.debug("Attempt 1: Searching with all available parameters")
        query = generate_query(equipment_type, 
                                origin_min_lat, 
                                origin_max_lat, 
                                origin_min_lng, 
                                origin_max_lng, 
                                destination_min_lat,
                                destination_max_lat,
                                destination_min_lng,
                                destination_max_lng,
                                pickup_datetime)
        
        result = query.execute()
        loads_data = result.data if result.data else []
        logger.debug(f"Attempt 1 returned {len(loads_data)} loads")
        
        if loads_data:
            logger.info(f"Found {len(loads_data)} loads for {equipment_type} near {origin} with all parameters")
            return loads_data, []
        
        # Attempt 2: Only if pickup_datetime was provided, retry without it
        if has_pickup_datetime:
            logger.debug("Attempt 2: Searching with equipment + origin + destination (no pickup_datetime)")
            query = generate_query(equipment_type, 
                                    origin_min_lat, 
                                    origin_max_lat, 
                                    origin_min_lng, 
                                    origin_max_lng, 
                                    destination_min_lat,
                                    destination_max_lat,
                                    destination_min_lng,
                                    destination_max_lng,
                                    None)  # No pickup_datetime
            
            result = query.execute()
            loads_data = result.data if result.data else []
            logger.debug(f"Attempt 2 returned {len(loads_data)} loads")
            
            if loads_data:
                logger.info(f"Found {len(loads_data)} loads for {equipment_type} near {origin} with equipment + origin + destination")
                omitted_parameters: list[str] = []
                if originally_provided_pickup:
                    omitted_parameters.append("pickup_datetime")
                return loads_data, omitted_parameters
        
        # Attempt 3: Only if destination was provided, retry without destination
        if has_destination:
            logger.debug("Attempt 3: Searching with equipment + origin only")
            query = generate_query(equipment_type, 
                                    origin_min_lat, 
                                    origin_max_lat, 
                                    origin_min_lng, 
                                    origin_max_lng, 
                                    None,  # No destination
                                    None,
                                    None,
                                    None,
                                    None)  # No pickup_datetime
            
            result = query.execute()
            loads_data = result.data if result.data else []
            logger.debug(f"Attempt 3 returned {len(loads_data)} loads")
            
            if loads_data:
                logger.info(f"Found {len(loads_data)} loads for {equipment_type} near {origin} with equipment + origin only")
                omitted_parameters: list[str] = []
                if originally_provided_destination:
                    omitted_parameters.append("destination")
                if originally_provided_pickup:
                    omitted_parameters.append("pickup_datetime")
                return loads_data, omitted_parameters
        else:
            logger.info(f"No loads found for {equipment_type} near {origin} after all retry attempts")
            return [], []

    except Exception as e:
        logger.error(f"Error in find_loads_within_radius: {str(e)}")
        logger.debug("Returning empty loads list due to error")
        return [], []

def process_parameters(equipment_type: str, pickup_datetime: str | None = None) -> str:
    """Process the parameters and return the processed values"""
    logger.debug(f"Processing parameters - Equipment: {equipment_type}, Pickup: {pickup_datetime}")
    # normalize the equipment type (lower and remove spaces)
    equipment_type = equipment_type.lower()
    equipment_type = equipment_type.replace(" ", "")

    # validate pickup datetime (ISO format)
    # Treat empty strings as absent
    if isinstance(pickup_datetime, str) and pickup_datetime.strip() == "":
        pickup_datetime = None
    if pickup_datetime:
        try:
            pickup_datetime = datetime.fromisoformat(pickup_datetime)
        except ValueError:
            logger.error(f"Invalid pickup datetime: {pickup_datetime}")
            raise ValueError("Invalid pickup datetime")

    return equipment_type, pickup_datetime