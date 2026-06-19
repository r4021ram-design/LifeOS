from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response, APIRouter

# Prometheus Metrics Definitions
API_REQUESTS = Counter(
    "lifeos_api_requests_total",
    "Total count of incoming API requests",
    ["method", "endpoint", "status"]
)

API_LATENCY = Histogram(
    "lifeos_api_latency_seconds",
    "Latency of API requests in seconds",
    ["method", "endpoint"]
)

DB_QUERY_TIME = Histogram(
    "lifeos_db_query_seconds",
    "Time taken to execute database queries in seconds"
)

REDIS_LATENCY = Histogram(
    "lifeos_redis_latency_seconds",
    "Time taken for Redis cache hits/writes in seconds"
)

AI_DURATION = Histogram(
    "lifeos_ai_request_seconds",
    "Time spent communicating with AI providers",
    ["provider", "model"]
)

PANCHANG_DURATION = Histogram(
    "lifeos_panchang_calc_seconds",
    "Time taken to compute Panchang variables"
)

metrics_router = APIRouter(prefix="/metrics", tags=["monitoring"])

@metrics_router.get("/")
def get_metrics():
    """Exposes Prometheus registry metrics formatted output."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
