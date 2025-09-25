"""
ResQConnect NLP Services
Handles intent extraction, entity recognition, and geocoding
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import re
import json
import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import redis
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ResQConnect NLP Service",
    description="Intent extraction, entity recognition, and geocoding",
    version="1.0.0"
)

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

# Geocoder
geolocator = Nominatim(user_agent="resqconnect-nlp")

class Entity(BaseModel):
    label: str
    text: str
    confidence: float

class Location(BaseModel):
    lat: float
    lon: float
    confidence: float
    address: Optional[str] = None

class NLPRequest(BaseModel):
    request_id: str
    text: str
    source: str
    existing_location: Optional[Dict[str, float]] = None

class NLPResponse(BaseModel):
    request_id: str
    intent: str
    entities: List[Entity]
    location: Optional[Location]
    urgency: int  # 1-10 scale
    confidence: float
    processed_text: str

# Simple rule-based NLP (in production, use trained models)
INTENT_PATTERNS = {
    "request_supply": [
        r"\b(need|want|require|looking for)\b.*\b(water|food|medicine|medical|blanket|shelter|clothes)\b",
        r"\b(hungry|thirsty|cold|sick|injured)\b",
        r"\b(help|assistance|aid|support)\b"
    ],
    "request_rescue": [
        r"\b(trapped|stuck|stranded|rescue|save)\b",
        r"\b(building collapsed|under debris|can't move)\b",
        r"\b(emergency|urgent|critical)\b"
    ],
    "offer_help": [
        r"\b(volunteer|help others|can provide|offering|available)\b",
        r"\b(have supplies|can transport|medical professional)\b"
    ],
    "report_status": [
        r"\b(safe|okay|fine|all good|no help needed)\b",
        r"\b(status update|checking in)\b"
    ]
}

ENTITY_PATTERNS = {
    "item": [
        r"\b(water|food|medicine|medical supplies|blanket|shelter|clothes|battery|flashlight|radio)\b",
        r"\b(insulin|bandages|antibiotics|pain medication)\b"
    ],
    "location": [
        r"\b(at|near|in|on)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",
        r"\b(\d+\s+[A-Za-z\s]+(?:street|road|avenue|lane|drive|way))\b"
    ],
    "urgency": [
        r"\b(urgent|emergency|critical|immediate|asap|now)\b",
        r"\b(life threatening|dying|severe|critical condition)\b"
    ],
    "quantity": [
        r"\b(\d+)\s+(people|person|family|families|children|adults)\b",
        r"\b(many|few|several|multiple|single)\b"
    ]
}

def extract_intent(text: str) -> tuple[str, float]:
    """Extract intent from text using rule-based matching"""
    text_lower = text.lower()
    
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return intent, 0.8  # Rule-based confidence
    
    return "request_supply", 0.3  # Default intent with low confidence

def extract_entities(text: str) -> List[Entity]:
    """Extract entities from text"""
    entities = []
    text_lower = text.lower()
    
    for entity_type, patterns in ENTITY_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                entity_text = match.group(1) if match.groups() else match.group(0)
                entities.append(Entity(
                    label=entity_type,
                    text=entity_text,
                    confidence=0.7
                ))
    
    return entities

def calculate_urgency(text: str, intent: str, entities: List[Entity]) -> int:
    """Calculate urgency score 1-10"""
    urgency = 5  # Default medium urgency
    text_lower = text.lower()
    
    # Intent-based urgency
    if intent == "request_rescue":
        urgency = 9
    elif intent == "request_supply":
        urgency = 6
    elif intent == "offer_help":
        urgency = 3
    elif intent == "report_status":
        urgency = 2
    
    # Entity-based adjustments
    for entity in entities:
        if entity.label == "urgency":
            if "critical" in entity.text or "emergency" in entity.text:
                urgency = min(10, urgency + 3)
            elif "urgent" in entity.text:
                urgency = min(10, urgency + 2)
    
    # Keyword-based adjustments
    if any(word in text_lower for word in ["dying", "life threatening", "critical condition"]):
        urgency = 10
    elif any(word in text_lower for word in ["trapped", "stuck", "can't move"]):
        urgency = min(10, urgency + 2)
    elif any(word in text_lower for word in ["children", "baby", "elderly"]):
        urgency = min(10, urgency + 1)
    
    return max(1, min(10, urgency))

def geocode_location(text: str, existing_location: Optional[Dict[str, float]] = None) -> Optional[Location]:
    """Extract and geocode location from text"""
    if existing_location:
        return Location(
            lat=existing_location["lat"],
            lon=existing_location["lon"],
            confidence=0.9,
            address="User provided"
        )
    
    # Extract location mentions from text
    location_patterns = [
        r"\b(?:at|near|in|on)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",
        r"\b(\d+\s+[A-Za-z\s]+(?:street|road|avenue|lane|drive|way))\b"
    ]
    
    for pattern in location_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            location_text = match.group(1)
            try:
                location = geolocator.geocode(location_text, timeout=5)
                if location:
                    return Location(
                        lat=location.latitude,
                        lon=location.longitude,
                        confidence=0.6,
                        address=location.address
                    )
            except GeocoderTimedOut:
                logger.warning(f"Geocoding timeout for: {location_text}")
                continue
    
    return None

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nlp-service"}

@app.post("/nlp/process", response_model=NLPResponse)
async def process_text(request: NLPRequest):
    """Process text for intent, entities, and location"""
    try:
        # Extract intent
        intent, intent_confidence = extract_intent(request.text)
        
        # Extract entities
        entities = extract_entities(request.text)
        
        # Calculate urgency
        urgency = calculate_urgency(request.text, intent, entities)
        
        # Geocode location
        location = geocode_location(request.text, request.existing_location)
        
        # Overall confidence (simple average)
        overall_confidence = (intent_confidence + sum(e.confidence for e in entities) / max(len(entities), 1)) / 2
        
        response = NLPResponse(
            request_id=request.request_id,
            intent=intent,
            entities=entities,
            location=location,
            urgency=urgency,
            confidence=overall_confidence,
            processed_text=request.text.strip()
        )
        
        logger.info(f"Processed NLP for request {request.request_id}: intent={intent}, urgency={urgency}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing NLP for {request.request_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="NLP processing failed")

@app.get("/nlp/intents")
async def get_supported_intents():
    """Get list of supported intents"""
    return {
        "intents": list(INTENT_PATTERNS.keys()),
        "entities": list(ENTITY_PATTERNS.keys())
    }

@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint"""
    return {
        "requests_processed": redis_client.get("nlp:requests_processed") or 0,
        "average_confidence": redis_client.get("nlp:avg_confidence") or 0.0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8086)