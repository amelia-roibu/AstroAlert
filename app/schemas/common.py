from datetime import date
from pydantic import BaseModel

class AstronomicalEventBase(BaseModel):
    id: str
    name: str
    event_date: date
    source: str