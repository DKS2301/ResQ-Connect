"""
ResQConnect Ingest Service
Handles SMS, WhatsApp, and form submissions for disaster relief requests
"""

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import redis
import hashlib
import uuid
from datetime import datetime
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ResQConnect Ingest Service",
    description="SMS/WhatsApp/Form ingestion for disaster relief requests",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection for deduplication
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

class IngestRequest(BaseModel):
    source: str  # sms, whatsapp, form, ivr
    phone_number: Optional[str] = None
    message: str
    location: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None

class IngestResponse(BaseModel):
    request_id: str
    status: str
    message: str

def hash_phone_number(phone: str) -> str:
    """Hash phone number for privacy"""
    return hashlib.sha256(phone.encode()).hexdigest()[:16]

def generate_request_id() -> str:
    """Generate unique request ID"""
    return f"req-{uuid.uuid4().hex[:8]}"

def deduplicate_request(phone_hash: str, message: str) -> bool:
    """Check if this is a duplicate request within 5 minutes"""
    key = f"dedupe:{phone_hash}:{hashlib.md5(message.encode()).hexdigest()[:8]}"
    if redis_client.exists(key):
        return True
    redis_client.setex(key, 300, "1")  # 5 minute expiry
    return False

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ingest-service"}

@app.post("/ingest/sms", response_model=IngestResponse)
async def ingest_sms(request: IngestRequest):
    """Ingest SMS requests"""
    try:
        if not request.phone_number:
            raise HTTPException(status_code=400, detail="Phone number required for SMS")
        
        phone_hash = hash_phone_number(request.phone_number)
        
        # Check for duplicates
        if deduplicate_request(phone_hash, request.message):
            logger.info(f"Duplicate SMS request from {phone_hash}")
            return IngestResponse(
                request_id="duplicate",
                status="duplicate",
                message="Request already received"
            )
        
        request_id = generate_request_id()
        
        # Store raw payload
        payload = {
            "request_id": request_id,
            "source": "sms",
            "phone_hash": phone_hash,
            "message": request.message,
            "location": request.location,
            "metadata": request.metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
            "processed": False
        }
        
        # Store in Redis for processing
        redis_client.setex(f"raw:{request_id}", 3600, json.dumps(payload))
        
        # Publish to event bus (simulated with Redis pub/sub for now)
        redis_client.publish("ingest.raw", json.dumps(payload))
        
        logger.info(f"SMS request ingested: {request_id}")
        
        return IngestResponse(
            request_id=request_id,
            status="received",
            message="Your request has been received and is being processed"
        )
        
    except Exception as e:
        logger.error(f"Error ingesting SMS: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/ingest/whatsapp", response_model=IngestResponse)
async def ingest_whatsapp(request: IngestRequest):
    """Ingest WhatsApp requests"""
    try:
        if not request.phone_number:
            raise HTTPException(status_code=400, detail="Phone number required for WhatsApp")
        
        phone_hash = hash_phone_number(request.phone_number)
        
        # Check for duplicates
        if deduplicate_request(phone_hash, request.message):
            logger.info(f"Duplicate WhatsApp request from {phone_hash}")
            return IngestResponse(
                request_id="duplicate",
                status="duplicate",
                message="Request already received"
            )
        
        request_id = generate_request_id()
        
        # Store raw payload
        payload = {
            "request_id": request_id,
            "source": "whatsapp",
            "phone_hash": phone_hash,
            "message": request.message,
            "location": request.location,
            "metadata": request.metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
            "processed": False
        }
        
        # Store in Redis for processing
        redis_client.setex(f"raw:{request_id}", 3600, json.dumps(payload))
        
        # Publish to event bus
        redis_client.publish("ingest.raw", json.dumps(payload))
        
        logger.info(f"WhatsApp request ingested: {request_id}")
        
        return IngestResponse(
            request_id=request_id,
            status="received",
            message="Your request has been received and is being processed"
        )
        
    except Exception as e:
        logger.error(f"Error ingesting WhatsApp: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/ingest/form", response_model=IngestResponse)
async def ingest_form(
    message: str = Form(...),
    phone_number: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None)
):
    """Ingest web form requests"""
    try:
        request_id = generate_request_id()
        
        location = None
        if latitude and longitude:
            location = {"lat": latitude, "lon": longitude}
        
        phone_hash = None
        if phone_number:
            phone_hash = hash_phone_number(phone_number)
            
            # Check for duplicates
            if deduplicate_request(phone_hash, message):
                logger.info(f"Duplicate form request from {phone_hash}")
                return IngestResponse(
                    request_id="duplicate",
                    status="duplicate",
                    message="Request already received"
                )
        
        # Store raw payload
        payload = {
            "request_id": request_id,
            "source": "form",
            "phone_hash": phone_hash,
            "message": message,
            "location": location,
            "metadata": {},
            "timestamp": datetime.utcnow().isoformat(),
            "processed": False
        }
        
        # Store in Redis for processing
        redis_client.setex(f"raw:{request_id}", 3600, json.dumps(payload))
        
        # Publish to event bus
        redis_client.publish("ingest.raw", json.dumps(payload))
        
        logger.info(f"Form request ingested: {request_id}")
        
        return IngestResponse(
            request_id=request_id,
            status="received",
            message="Your request has been received and is being processed"
        )
        
    except Exception as e:
        logger.error(f"Error ingesting form: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # Basic metrics - in production, use prometheus_client
    return {
        "requests_total": redis_client.get("metrics:requests_total") or 0,
        "duplicates_total": redis_client.get("metrics:duplicates_total") or 0,
        "errors_total": redis_client.get("metrics:errors_total") or 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085)