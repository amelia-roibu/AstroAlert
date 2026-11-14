# aici avem data models

from datetime import date
from pydantic import BaseModel
from app.schemas.common import AstronomicalEventBase


# definim 2 modele Pydantic
class NeoEvent(AstronomicalEventBase):
    external_id: str
    close_approach_date: date
    is_potentially_hazardous: bool
    estimated_diameter_km: float # in km
    miss_distance_km: float # in km
    relative_velocity_km_h: float # in km/h
    orbiting_body: str
    # o valoare numerica fara unitate poate produce confuzii si erori de interpretare

# raspunsul complet al endpointului
class NeoFeedResponse(BaseModel):
    start_date: date
    total_events: int
    events: list[NeoEvent]