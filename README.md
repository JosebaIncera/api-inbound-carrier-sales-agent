# Carrier Sales API

A FastAPI-based service for carrier validation and load matching in the transportation/logistics industry. This API provides comprehensive functionality for validating motor carriers, finding matching loads, and tracking metrics for sales operations.

## Features

- **Carrier Validation**: Validate MC numbers and verify carrier existence in database
- **Load Matching**: Find available loads based on equipment type, origin, and other criteria
- **Metrics Tracking**: Store and retrieve call outcomes, sentiment analysis, and negotiation data
- **API Key Authentication**: Secure access control for all endpoints
- **Comprehensive Logging**: Detailed logging with performance metrics
- **Supabase Integration**: Robust database operations with PostgreSQL

## API Endpoints

### Carrier Management (`/carriers`)

#### `GET /carriers/validate_carrier`
Validates Motor Carrier (MC) numbers and checks carrier existence in the database.

**Parameters:**
- `mc_number` (required): MC number in format "MC XXXXXX"
- `api_key` (required): Authentication key

**Response:** `CarrierResponse`
```json
{
  "statusCode": 200,
  "verified_carrier": true,
  "message": "MC number MC 123456 is valid and carrier exists in database"
}
```

#### `GET /carriers/carriers`
Retrieves carrier information (placeholder implementation).

**Parameters:**
- `api_key` (required): Authentication key

### Load Management (`/loads`)

#### `GET /loads/find_matching_loads`
Finds available loads matching specified criteria.

**Parameters:**
- `equipment_type` (required): Type of equipment needed
- `origin` (required): Starting location
- `destination` (optional): Delivery location
- `pickup_datetime` (optional): Preferred pickup date/time
- `api_key` (required): Authentication key

**Response:** `LoadsResponse`
```json
{
  "statusCode": 200,
  "loads_available": true,
  "message": "Number of available loads: 5",
  "loads": [
    {
      "load_id": "uuid-string",
      "origin_city": "Chicago",
      "origin_state": "IL",
      "destination_city": "Los Angeles",
      "destination_state": "CA",
      "pickup_datetime": "2024-01-15T08:00:00Z",
      "equipment_type": "Dry Van",
      "loadboard_rate": 2500.00,
      "weight": 45000.0,
      "miles": 2000.0
    }
  ],
  "omitted_parameters": []
}
```

### Metrics Management (`/metrics`)

#### `GET /metrics/get_metrics`
Retrieves stored metrics data.

**Parameters:**
- `api_key` (required): Authentication key

#### `POST /metrics/store_metrics`
Stores new metrics data for tracking call outcomes.

**Request Body:** `MetricsRequest`
```json
{
  "call_outcome": "Booked",
  "carrier_sentiment": "Positive",
  "load_loadboard_rate": 2500.00,
  "carrier_initial_offer": 2400.00,
  "load_agreed_rate": 2450.00,
  "negotiation_attempts": 2,
  "run_id": "run-123",
  "organization_id": "org-456"
}
```

#### `POST /metrics/update_metrics`
Updates existing metrics with HappyRobot data (runs as background process).

**Parameters:**
- `api_key` (required): Authentication key

### System Endpoints

#### `GET /health`
Root health check endpoint returning service status and version information.

#### `GET /`
Root endpoint for basic service availability check.

## Installation & Setup

### Prerequisites
- Python 3.8+
- Docker (optional)
- Supabase account and database

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd api-inbound-carrier-sales-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   # Create .env file with required variables
   API_KEY=your-api-key
   SUPABASE_URL=your-supabase-url
   SUPABASE_KEY=your-supabase-key
   DEBUG=true
   ```

4. **Run the application**
   ```bash
   python -m app.main
   ```

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t carrier-sales-api .
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

## Configuration

The API uses environment variables for configuration:

- `API_KEY`: Required API key for authentication
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase service role key
- `DEBUG`: Enable debug logging (true/false)

## Authentication

All endpoints require API key authentication. Include the API key as a query parameter:

```
GET /carriers/validate_carrier?mc_number=MC%20123456&api_key=your-api-key
```

## Error Handling

The API provides standardized error responses:

- **400 Bad Request**: Invalid parameters or request format
- **401 Unauthorized**: Missing or invalid API key
- **500 Internal Server Error**: Server-side errors with detailed logging

## Logging

The API includes comprehensive logging:

- **Request/Response logging**: All API calls are logged with timing
- **Error logging**: Detailed error information for debugging
- **Performance metrics**: Request processing times tracked
- **Configurable levels**: DEBUG, INFO, WARNING, ERROR levels

## Database Schema

The API integrates with Supabase (PostgreSQL) for:

- **Carrier data**: MC number validation and storage
- **Load data**: Available loads with detailed information
- **Metrics data**: Call outcomes, sentiment, and negotiation tracking

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Development

### Project Structure
```
app/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management
├── auth.py              # Authentication middleware
├── middleware.py        # Custom middleware
├── supabase.py          # Database connection
├── routers/             # API route handlers
│   ├── carriers.py      # Carrier management endpoints
│   ├── loads.py         # Load management endpoints
│   └── metrics.py       # Metrics tracking endpoints
├── schemas/             # Pydantic data models
│   └── schemas.py       # Request/response models
└── utils/               # Utility functions
    ├── utils_carriers.py
    ├── utils_loads.py
    └── utils_metrics.py
```

### Testing

Run tests using pytest:
```bash
pytest tests/
```
