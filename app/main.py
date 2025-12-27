from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from app.core.config import settings
from app.api.endpoints import router as api_router
import os
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY

# Prometheus metrics - using a function with try-except to avoid duplicate registration
def get_metrics():
    try:
        request_count = Counter(
            "http_requests_total", 
            "Total HTTP Requests", 
            ["method", "endpoint", "http_status"]
        )
    except ValueError:
        # If already registered, find it in the registry
        for collector in REGISTRY._collector_to_names:
            if hasattr(collector, "_name") and collector._name == "http_requests_total":
                request_count = collector
                break
        else:
            # Fallback if not found but still raising ValueError
            # This shouldn't happen but for safety:
            request_count = Counter("http_requests_total_alt", "Total HTTP Requests", ["method", "endpoint", "http_status"])

    try:
        request_latency = Histogram(
            "http_request_duration_seconds", 
            "HTTP Request Latency", 
            ["method", "endpoint"]
        )
    except ValueError:
        for collector in REGISTRY._collector_to_names:
            if hasattr(collector, "_name") and collector._name == "http_request_duration_seconds":
                request_latency = collector
                break
        else:
            request_latency = Histogram("http_request_duration_seconds_alt", "HTTP Request Latency", ["method", "endpoint"])
            
    return request_count, request_latency

REQUEST_COUNT, REQUEST_LATENCY = get_metrics()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    endpoint = request.url.path
    method = request.method
    status_code = response.status_code
    
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status_code).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
    
    # Add latency metadata to response headers as required in P0.2
    response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "unknown")
    response.headers["X-API-Latency-MS"] = str(int(duration * 1000))
    
    return response

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"{settings.API_V1_STR}/health")

@app.get("/stats")
def stats_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"{settings.API_V1_STR}/stats")

@app.get("/")
def root():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to Kasparro API", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable for Render/Heroku compatibility
    port = int(os.environ.get("PORT", 8000))
    
    # Run uvicorn
    # Reduced workers to 1 for stability in limited resource environments
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="info")
