# Pydantic Models
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class MCValidationResponse(BaseModel):
    valid: bool
    mc_number: str
    message: str

class LoadConstraints(BaseModel):
    equipment_type: str
    origin: str
    destination: Optional[str] = None
    pickup_datetime: Optional[str] = None
    delivery_datetime: Optional[str] = None
    min_rate: Optional[float] = None
    max_rate: Optional[float] = None
    weight: Optional[int] = None
    commodity_type: Optional[str] = None
    miles: Optional[int] = None

class LoadsRequest(BaseModel):
    load_constraints: LoadConstraints

class LoadAvailabilityResponse(BaseModel):
    loads_available: bool
    message: str

class LoadResponse(BaseModel):
    load_id: str  # UUID serialized as string
    origin_city: str
    origin_state: Optional[str] = None
    destination_city: str
    destination_state: Optional[str] = None
    pickup_datetime: Optional[str] = None  # timestamp with time zone
    delivery_datetime: Optional[str] = None  # timestamp with time zone
    equipment_type: Optional[str] = None
    loadboard_rate: Optional[float] = None  # numeric -> float
    notes: Optional[str] = None
    weight: Optional[float] = None  # numeric -> float (was int)
    commodity_type: Optional[str] = None
    num_of_pieces: Optional[int] = None
    miles: Optional[float] = None  # numeric -> float (was int)
    dimensions: Optional[str] = None
    created_at: Optional[str] = None  # timestamp with time zone - was missing
    origin_lat: Optional[float] = None
    origin_lng: Optional[float] = None
    destination_lat: Optional[float] = None
    destination_lng: Optional[float] = None

class LoadsResponse(BaseModel):
    statusCode: int
    loads_available: bool
    message: str
    loads: List[LoadResponse]
    omitted_parameters: List[str] = Field(default_factory=list)

class CarrierResponse(BaseModel):
    statusCode: int
    verified_carrier: bool
    message: str

class NegotiateRequest(BaseModel):
    load_id: str
    carrier_mc: str
    proposed_rate: float
    notes: Optional[str] = None

class NegotiateResponse(BaseModel):
    negotiation_id: str
    load_id: str
    carrier_mc: str
    proposed_rate: float
    counter_rate: Optional[float] = None
    status: str  # "accepted", "countered", "rejected"
    message: str

class ConfirmRequest(BaseModel):
    load_id: str
    carrier_mc: str
    final_rate: float
    confirmation_notes: Optional[str] = None

class ConfirmResponse(BaseModel):
    confirmation_id: str
    load_id: str
    carrier_mc: str
    final_rate: float
    status: str
    booking_reference: str
    message: str

class MetricsRequest(BaseModel):
    call_outcome: str  # "No Match", "Booked", "Rejected", etc.
    carrier_sentiment: str  # "Neutral", "Positive", "Negative"
    load_loadboard_rate: Optional[float] = None
    carrier_initial_offer: Optional[float] = None
    load_agreed_rate: Optional[float] = None
    negotiation_attempts: Optional[int] = None
    run_id: str
    organization_id: str

class MetricsResponse(BaseModel):
    statusCode: int
    success: Optional[bool] = True
    message: Optional[str] = "Success"
    metrics: Optional[List[Dict[str, Any]]] = None


class MetricsStatsResponse(BaseModel):
    total_calls: int
    successful_bookings: int
    average_call_duration: float
    success_rate: float
    top_carriers: List[Dict[str, Any]]
    outcome_breakdown: Dict[str, int]