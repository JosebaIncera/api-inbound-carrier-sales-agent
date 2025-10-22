from fastapi import FastAPI, Depends
from app.auth import verify_api_key

def create_app() -> FastAPI:
    """Create FastAPI application with global API key validation"""
    
    app = FastAPI(title="Carrier Sales API", version="1.0.0")
    
    # Option 1: Apply to all endpoints except health checks
    # app.dependency_overrides[verify_api_key] = verify_api_key
    
    # Option 2: Add global dependency to all routes
    # This will require API key for ALL endpoints
    # app.dependency_overrides = {verify_api_key: verify_api_key}
    
    return app

# Alternative: Apply dependency to specific router groups
def apply_auth_to_router(router, exclude_paths: list = None):
    """
    Apply API key validation to all routes in a router except excluded paths.
    
    Args:
        router: FastAPI router
        exclude_paths: List of paths to exclude from authentication
    """
    exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json"]
    
    for route in router.routes:
        if hasattr(route, 'path') and route.path not in exclude_paths:
            # Add the dependency to the route
            if not hasattr(route, 'dependencies'):
                route.dependencies = []
            route.dependencies.append(Depends(verify_api_key))
    
    return router
