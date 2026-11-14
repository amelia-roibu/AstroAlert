from datetime import date
import logging
import httpx
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.config import NASA_API_URL, NASA_API_KEY
from app.schemas.neo import NeoFeedResponse
from app.services.nasa import normalize_neo_feed
from app.services.filtering import filter_neo_events
from app.services.persistence import persist_neo_events
from app.database.connection import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api",
                   tags=["Astronomical Events"])
# tagurile sunt folosite in principal pentru organizarea documentatiei interactive Swagger

@router.get("/neo", response_model=NeoFeedResponse)
# folosim async def pt ca serverul sa poata gestiona si alte operatii
# in timp ce asteapta raspunsul NASA, ca sa nu blocheze executia
def get_nasa_neo(start_date: date = Query(default_factory=date.today), # aici se transmite numele functiei, adica today()
                hazardous_only: bool = Query(default=False),
                max_distance_km: float | None = Query(default=None, gt=0),
                min_diameter_km: float | None = Query(default=None, gt=0),
                min_velocity_km_h: float | None = Query(default=None, gt=0),
                db: Session = Depends(get_db),):
    if not NASA_API_KEY:
        raise HTTPException(status_code=500,
                            detail="NASA API key is not configured")

    params = {"start_date": start_date.isoformat(),
              "api_key": NASA_API_KEY}

    try:
        # httpx.AsyncClient deschide un client HTTP asincron
        with httpx.Client(timeout=15.0) as client:
            # trimite cererea catre NASA si asteapta raspunsul
            response = client.get(NASA_API_URL, params=params)
            # verificam daca NASA a raspuns cu un cod HTTP de succes
            # daca raspunsul indica o eroare, se genereaza o exceptie
            response.raise_for_status()
            nasa_data = response.json()

    except httpx.HTTPStatusError as error:
        raise HTTPException (status_code=502,
                             detail="NASA API returned an error") from error
    # daca n-am reusit sa comunicam cu NASA, de ex din cauza unei probleme de retea
    except httpx.RequestError as error:
        raise HTTPException(status_code=503,
                            detail="NASA API is currently unvailable") from error

    except ValueError as error:
        raise HTTPException(status_code=502,
                            detail="NASA API returned invalid JSON",) from error

    try:
        events = normalize_neo_feed(nasa_data)

    except (KeyError, TypeError, ValueError) as error:
        raise HTTPException(status_code=502,
                            detail="NASA API returned an unexpected data format") from error

    try:
        persist_neo_events(db, events)

    except SQLAlchemyError as error:
        logger.exception("Database error while persisting NEO events")
        raise HTTPException (status_code=500,
                             detail="Could not save astronomical events",) from error

    filtered_events = filter_neo_events(events=events,
                                        hazardous_only=hazardous_only,
                                        max_distance_km=max_distance_km,
                                        min_diameter_km=min_diameter_km,
                                        min_velocity_km_h=min_velocity_km_h)

    return NeoFeedResponse(start_date=start_date,
                           total_events=len(events),
                           events=filtered_events)