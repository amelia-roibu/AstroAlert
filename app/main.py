# aici integram HTTP endpoints si API layer
# adica va conecta componentele la endpoint-urile API

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from app.routers.neo import router as neo_router
from app.routers.eclipses import router as eclipses_router

app = FastAPI( title="AstroAlert",
               description="Astronomical Event Monitoring Platform",
               version="0.1.0")

app.include_router(neo_router)
app.include_router(eclipses_router)

class AlertCreate(BaseModel):
    email: str = Field(min_length=5)
    max_distance_km: float = Field(gt=0)
    hazardous_only: bool = False

@app.get("/")
def home():
    return {"message": "Welcome to AstroAlert!"}

@app.get("/health")
def health_check():
    return {"status": "healthy",
            "application": "AstroAlert",
            "version": "0.1.0"}

@app.get("/events/{event_id}")
def get_event(event_id:str):
    return { "event_id": event_id,
             "message": "Event details requested"
    }

# sample for astronomy dataset
sample_events = [
    {
        "id": "NEO-001",
        "name": "Asteroid Alpha",
        "hazardous": True,
        "distance_km": 850000
    },
    {
        "id": "NEO-002",
        "name": "Asteroid Beta",
        "hazardous": False,
        "distance_km": 2400000
    },
    {
        "id": "NEO-003",
        "name": "Asteroid Gamma",
        "hazardous": True,
        "distance_km": 500000
    }
]

@app.get("/events")
def get_events(hazardous: bool | None = None,
               min_distance_km: float | None = Query(default=None, gt=0)):
    filtered_events = sample_events

    if hazardous is not None:
        filtered_events = [event for event in filtered_events if event["hazardous"]==hazardous]

    if min_distance_km is not None:
        filtered_events = [event for event in filtered_events if event["distance_km"] >= min_distance_km]

    return {
        "total": len(filtered_events),
        "events": filtered_events
    }

@app.post("/alerts", status_code=201)
def create_alert(alert: AlertCreate):
    return { "message": "Alert configuration received",
             "alert": alert }