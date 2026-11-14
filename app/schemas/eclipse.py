from datetime import time
from typing import Literal
from pydantic import BaseModel
from app.schemas.common import AstronomicalEventBase

class EclipseEvent(AstronomicalEventBase):
    eclipse_type: Literal["solar", "lunar"]
    eclipse_subtype: str
    greatest_eclipse_td: time | None = None
    magnitude: float | None = None
    saros_number: int | None = None
    duration: str | None = None
    visibility_regions: str | None = None

# raspunsul endpointului care va returna lista de eclipse in parametri
class EclipseListResponse(BaseModel):
    start_year: int
    end_year: int
    total_events: int
    events: list[EclipseEvent]