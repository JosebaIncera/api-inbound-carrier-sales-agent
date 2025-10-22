from fastapi import FastAPI
from app.routers import carriers, loads
from app.config import settings
import logging
import uvicorn
from datetime import datetime
from datetime import timezone
import sys

# Configure comprehensive logging
log_handlers = [logging.StreamHandler(sys.stdout)]
if settings.debug:  # or an env flag like os.getenv("LOG_TO_FILE") == "true"
    log_handlers.append(logging.FileHandler('app.log', mode='a'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=log_handlers
)

# Set different log levels for different modules
logger = logging.getLogger(__name__)
logging.getLogger("app.routers.carriers").setLevel(logging.INFO)
logging.getLogger("app.routers.loads").setLevel(logging.INFO)
logging.getLogger("app.utils").setLevel(logging.DEBUG)
logging.getLogger("app.auth").setLevel(logging.INFO)

app = FastAPI(
    title="Carrier Sales API", 
    version="1.0.0",
    description="API for carrier validation and load matching with API key authentication"
)

# Root health check endpoint
@app.get("/health")
async def health_check():
    """Root health check endpoint"""
    return {
        "status": "healthy",
        "service": "Carrier Sales API",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": "running"
    }

# Include routers
app.include_router(carriers.router)
app.include_router(loads.router)

# Log configuration on startup
@app.on_event("startup")
async def startup_event():
    logger.info("=" * 50)
    logger.info("Starting Carrier Sales API v1.0.0")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API Key configured: {'Yes' if settings.api_key else 'No'}")
    logger.info("Logging configured - INFO level for routers, DEBUG level for utils")
    logger.info("=" * 50)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)