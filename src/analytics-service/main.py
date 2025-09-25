"""
ResQConnect Analytics Service
Data pipeline, reporting, and analytics for disaster relief operation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import pandas as pd
import numpy as np
import json
import redis
import logging
import os
from datetime import datetime, timedelta
import asyncio
from sqlalchemy import create_engine, text
import plotly.graph_objects as go
import plotly.express as px
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ResQConnect Analytics Service",
    description="Data pipeline, reporting, and analytics",
    version="1.0.0"
)

# Prometheus metrics
requests_total = Counter('analytics_requests_total', 'Total analytics requests', ['endpoint'])
processing_time = Histogram('analytics_processing_seconds', 'Time spent processing analytics')
active_requests = Gauge('analytics_active_requests', 'Number of active disaster requests')
response_time_avg = Gauge('analytics_avg_response_time_minutes', 'Average response time in minutes')

# Database connections
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/resqconnect')
engine = create_engine(DATABASE_URL)

# Redis connection
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

class AnalyticsRequest(BaseModel):
    metric: str
    filters: Optional[Dict[str, Any]] = None
    time_range: Optional[Dict[str, str]] = None

class DashboardData(BaseModel):
    total_requests: int
    active_requests: int
    completed_requests: int
    total_volunteers: int
    active_volunteers: int
    avg_response_time: float
    requests_by_urgency: Dict[str, int]
    requests_by_type: Dict[str, int]
    geographic_distribution: List[Dict[str, Any]]

class ReportRequest(BaseModel):
    report_type: str
    start_date: str
    end_date: str
    filters: Optional[Dict[str, Any]] = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "analytics-service"}

@app.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data():
    """Get real-time dashboard data"""
    requests_total.labels(endpoint='dashboard').inc()
    
    try:
        with processing_time.time():
            # Get data from database
            with engine.connect() as conn:
                # Total requests
                total_requests_result = conn.execute(text("SELECT COUNT(*) FROM requests"))
                total_requests = total_requests_result.scalar() or 0
                
                # Active requests
                active_requests_result = conn.execute(text(
                    "SELECT COUNT(*) FROM requests WHERE status IN ('OPEN', 'ASSIGNED', 'IN_PROGRESS')"
                ))
                active_requests_count = active_requests_result.scalar() or 0
                
                # Completed requests
                completed_requests_result = conn.execute(text(
                    "SELECT COUNT(*) FROM requests WHERE status = 'COMPLETED'"
                ))
                completed_requests_count = completed_requests_result.scalar() or 0
                
                # Total volunteers
                total_volunteers_result = conn.execute(text("SELECT COUNT(*) FROM volunteers"))
                total_volunteers_count = total_volunteers_result.scalar() or 0
                
                # Active volunteers
                active_volunteers_result = conn.execute(text(
                    "SELECT COUNT(*) FROM volunteers WHERE available = true"
                ))
                active_volunteers_count = active_volunteers_result.scalar() or 0
                
                # Average response time
                avg_response_result = conn.execute(text("""
                    SELECT AVG(EXTRACT(EPOCH FROM (assigned_at - created_at))/60) 
                    FROM requests 
                    WHERE assigned_at IS NOT NULL AND created_at >= NOW() - INTERVAL '24 hours'
                """))
                avg_response = avg_response_result.scalar() or 0.0
                
                # Requests by urgency
                urgency_result = conn.execute(text("""
                    SELECT urgency, COUNT(*) 
                    FROM requests 
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                    GROUP BY urgency
                """))
                requests_by_urgency = {str(row[0]): row[1] for row in urgency_result}
                
                # Requests by type
                type_result = conn.execute(text("""
                    SELECT request_type, COUNT(*) 
                    FROM requests 
                    WHERE created_at >= NOW() - INTERVAL '24 hours'
                    GROUP BY request_type
                """))
                requests_by_type = {row[0]: row[1] for row in type_result}
                
                # Geographic distribution
                geo_result = conn.execute(text("""
                    SELECT 
                        ROUND(latitude::numeric, 2) as lat,
                        ROUND(longitude::numeric, 2) as lon,
                        COUNT(*) as count
                    FROM requests 
                    WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                    AND created_at >= NOW() - INTERVAL '24 hours'
                    GROUP BY ROUND(latitude::numeric, 2), ROUND(longitude::numeric, 2)
                    ORDER BY count DESC
                    LIMIT 50
                """))
                geographic_distribution = [
                    {"lat": row[0], "lon": row[1], "count": row[2]} 
                    for row in geo_result
                ]
        
        # Update Prometheus metrics
        active_requests.set(active_requests_count)
        response_time_avg.set(avg_response)
        
        return DashboardData(
            total_requests=total_requests,
            active_requests=active_requests_count,
            completed_requests=completed_requests_count,
            total_volunteers=total_volunteers_count,
            active_volunteers=active_volunteers_count,
            avg_response_time=avg_response,
            requests_by_urgency=requests_by_urgency,
            requests_by_type=requests_by_type,
            geographic_distribution=geographic_distribution
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

@app.get("/metrics/response-time")
async def get_response_time_metrics():
    """Get response time analytics"""
    requests_total.labels(endpoint='response-time').inc()
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    DATE_TRUNC('hour', created_at) as hour,
                    AVG(EXTRACT(EPOCH FROM (assigned_at - created_at))/60) as avg_response_time,
                    COUNT(*) as request_count
                FROM requests 
                WHERE assigned_at IS NOT NULL 
                AND created_at >= NOW() - INTERVAL '7 days'
                GROUP BY DATE_TRUNC('hour', created_at)
                ORDER BY hour
            """))
            
            data = [
                {
                    "hour": row[0].isoformat(),
                    "avg_response_time": float(row[1]) if row[1] else 0,
                    "request_count": row[2]
                }
                for row in result
            ]
            
        return {"response_time_trends": data}
        
    except Exception as e:
        logger.error(f"Error getting response time metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get response time metrics")

@app.get("/metrics/volunteer-efficiency")
async def get_volunteer_efficiency():
    """Get volunteer efficiency metrics"""
    requests_total.labels(endpoint='volunteer-efficiency').inc()
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    v.volunteer_id,
                    v.name,
                    COUNT(r.request_id) as completed_requests,
                    AVG(EXTRACT(EPOCH FROM (r.completed_at - r.assigned_at))/60) as avg_completion_time,
                    AVG(r.urgency) as avg_urgency_handled
                FROM volunteers v
                LEFT JOIN request_assignments ra ON v.volunteer_id = ra.volunteer_id
                LEFT JOIN requests r ON ra.request_id = r.request_id AND r.status = 'COMPLETED'
                WHERE r.completed_at >= NOW() - INTERVAL '30 days'
                GROUP BY v.volunteer_id, v.name
                HAVING COUNT(r.request_id) > 0
                ORDER BY completed_requests DESC
                LIMIT 20
            """))
            
            data = [
                {
                    "volunteer_id": row[0],
                    "name": row[1],
                    "completed_requests": row[2],
                    "avg_completion_time": float(row[3]) if row[3] else 0,
                    "avg_urgency_handled": float(row[4]) if row[4] else 0
                }
                for row in result
            ]
            
        return {"volunteer_efficiency": data}
        
    except Exception as e:
        logger.error(f"Error getting volunteer efficiency: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get volunteer efficiency")

@app.get("/reports/daily-summary")
async def get_daily_summary(date: Optional[str] = None):
    """Get daily summary report"""
    requests_total.labels(endpoint='daily-summary').inc()
    
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_requests,
                    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed_requests,
                    COUNT(CASE WHEN status IN ('OPEN', 'ASSIGNED') THEN 1 END) as pending_requests,
                    AVG(urgency) as avg_urgency,
                    COUNT(DISTINCT CASE WHEN status = 'COMPLETED' THEN assigned_volunteer_id END) as active_volunteers
                FROM requests 
                WHERE DATE(created_at) = :date
            """), {"date": date})
            
            row = result.fetchone()
            
            summary = {
                "date": date,
                "total_requests": row[0] or 0,
                "completed_requests": row[1] or 0,
                "pending_requests": row[2] or 0,
                "avg_urgency": float(row[3]) if row[3] else 0,
                "active_volunteers": row[4] or 0,
                "completion_rate": (row[1] / row[0] * 100) if row[0] > 0 else 0
            }
            
        return summary
        
    except Exception as e:
        logger.error(f"Error getting daily summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get daily summary")

@app.post("/reports/generate")
async def generate_report(report_request: ReportRequest, background_tasks: BackgroundTasks):
    """Generate custom report"""
    requests_total.labels(endpoint='generate-report').inc()
    
    # Add report generation to background tasks
    background_tasks.add_task(process_report_generation, report_request)
    
    return {
        "status": "accepted",
        "message": "Report generation started",
        "report_type": report_request.report_type
    }

async def process_report_generation(report_request: ReportRequest):
    """Background task to generate reports"""
    try:
        logger.info(f"Generating report: {report_request.report_type}")
        
        # Simulate report generation
        await asyncio.sleep(5)
        
        # Store report result in Redis
        report_data = {
            "report_type": report_request.report_type,
            "generated_at": datetime.now().isoformat(),
            "status": "completed",
            "data": {"placeholder": "Report data would be here"}
        }
        
        redis_client.setex(
            f"report:{report_request.report_type}:{datetime.now().strftime('%Y%m%d')}",
            3600,  # 1 hour expiry
            json.dumps(report_data)
        )
        
        logger.info(f"Report generated: {report_request.report_type}")
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")

@app.get("/analytics/trends")
async def get_trends():
    """Get trend analysis"""
    requests_total.labels(endpoint='trends').inc()
    
    try:
        with engine.connect() as conn:
            # Request trends over time
            result = conn.execute(text("""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as request_count,
                    AVG(urgency) as avg_urgency
                FROM requests 
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY DATE(created_at)
                ORDER BY date
            """))
            
            trends = [
                {
                    "date": row[0].isoformat(),
                    "request_count": row[1],
                    "avg_urgency": float(row[2]) if row[2] else 0
                }
                for row in result
            ]
            
        return {"trends": trends}
        
    except Exception as e:
        logger.error(f"Error getting trends: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get trends")

@app.get("/prometheus-metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest().decode('utf-8')

# Background task to update metrics periodically
async def update_metrics():
    """Background task to update Prometheus metrics"""
    while True:
        try:
            with engine.connect() as conn:
                # Update active requests metric
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM requests WHERE status IN ('OPEN', 'ASSIGNED', 'IN_PROGRESS')"
                ))
                active_count = result.scalar() or 0
                active_requests.set(active_count)
                
                # Update average response time
                result = conn.execute(text("""
                    SELECT AVG(EXTRACT(EPOCH FROM (assigned_at - created_at))/60) 
                    FROM requests 
                    WHERE assigned_at IS NOT NULL AND created_at >= NOW() - INTERVAL '1 hour'
                """))
                avg_response = result.scalar() or 0
                response_time_avg.set(avg_response)
                
        except Exception as e:
            logger.error(f"Error updating metrics: {str(e)}")
        
        await asyncio.sleep(60)  # Update every minute

# Start background task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_metrics())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8089)