import logging
import time
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from pythonjsonlogger import jsonlogger

# Logger setup
logger = logging.getLogger("eda-lab-api")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

app = FastAPI(title="Event-Driven Architecture Lab API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Path: {request.url.path} Duration: {duration:.4f}s Status: {response.status_code}")
    return response

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/events/publish")
def publish_event(topic: str, payload: dict):
    logger.info(f"Publishing event to {topic}")
    return {"status": "PUBLISHED", "message_id": f"msg_{int(time.time())}", "timestamp": time.time()}

@app.get("/events/topics")
def get_topics():
    return [
        {"name": "orders", "partitions": 3, "replication": 2},
        {"name": "payments", "partitions": 5, "replication": 3},
        {"name": "inventory", "partitions": 2, "replication": 2}
    ]

@app.post("/simulation/run")
def run_simulation(config: dict):
    logger.info(f"Running EDA simulation with config {config}")
    return {"status": "RUNNING", "simulation_id": f"sim_{int(time.time())}", "eta": "5m"}

@app.get("/metrics/throughput")
def get_throughput():
    return {
        "kafka_in": 12500,
        "kafka_out": 12480,
        "rabbitmq_in": 4500,
        "rabbitmq_out": 4495
    }

@app.get("/lag/summary")
def get_lag_summary():
    return {
        "shipping_service": 120,
        "invoice_service": 5,
        "analytics_service": 1450,
        "status": "ATTENTION_REQUIRED"
    }

@app.get("/scores/summary")
def get_scores_summary():
    return {
        "eda_maturity": 0.88,
        "reliability_score": 0.94,
        "latency_compliance": 0.99,
        "cost_efficiency": 0.91
    }

@app.get("/dashboard/summary")
def get_dashboard_summary():
    return {
        "total_producers": 45,
        "total_consumers": 124,
        "active_topics": 12,
        "lab_status": "OPERATIONAL"
    }
