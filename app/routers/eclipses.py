import logging
import httpx
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.connection import get_db
from app.schemas.eclipse import EclipseEvent, EclipseListResponse
from app.services.nasa_eclipses import parse_nasa_eclipses
from app.services.persistence import (persist_eclipse_events, is_eclipse_catalog_synced, mark_eclipse_catalog_synced, get_eclipse_events_from_db)
from app.services.filtering import filter_eclipse_events

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api",
                   tags=["Astronomical Events"])

NASA_CATALOGS = {
    "solar": {
        2020: "https://eclipse.gsfc.nasa.gov/SEdecade/SEdecade2011.html",
        2021: "https://eclipse.gsfc.nasa.gov/SEdecade/SEdecade2021.html",
        2031: "https://eclipse.gsfc.nasa.gov/SEdecade/SEdecade2031.html",
        2041: "https://eclipse.gsfc.nasa.gov/SEdecade/SEdecade2041.html",
    },
    "lunar": {
        2020: "https://eclipse.gsfc.nasa.gov/LEdecade/LEdecade2011.html",
        2021: "https://eclipse.gsfc.nasa.gov/LEdecade/LEdecade2021.html",
        2031: "https://eclipse.gsfc.nasa.gov/LEdecade/LEdecade2031.html",
        2041: "https://eclipse.gsfc.nasa.gov/LEdecade/LEdecade2041.html",
    }
}

def get_catalog_decade(year:int) -> int:
    if year == 2020:
        return 2020
    else:
        return ((year-1) // 10) * 10 + 1

def get_catalog_url(eclipse_type: str, year: int) -> str:
    decade_start = get_catalog_decade(year)
    return NASA_CATALOGS[eclipse_type][decade_start]

def fetch_catalog(eclipse_type: str, year: int) -> list[dict]:
    url = get_catalog_url(eclipse_type, year)

    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.get(url)
            response.raise_for_status()

    except httpx.HTTPStatusError as error:
        raise HTTPException (status_code=502,
                             detail="NASA catalog returned an error") from error

    except httpx.RequestError as error:
        raise HTTPException (status_code=503,
                             detail="NASA catalog is currently unavailable") from error

    try:
        return parse_nasa_eclipses(response.text, eclipse_type)

    except (KeyError, TypeError, ValueError) as error:
        logger.exception("Could not normalize NASA eclipse catalog")
        raise HTTPException (status_code=502,
                             detail="NASA catalog returned invalid eclipse data") from error

def synchronize_catalog(db: Session,eclipse_type: str,year: int) -> None:
    decade = get_catalog_decade(year)

    if is_eclipse_catalog_synced(db, eclipse_type, decade):
        return

    events = fetch_catalog(eclipse_type, year)

    normalized_events = [EclipseEvent(**event) for event in events]

    persist_eclipse_events(db, normalized_events)

    mark_eclipse_catalog_synced(db, eclipse_type, decade)

def get_eclipses(db: Session,
                 eclipse_type: str,
                 year: int,
                 eclipse_subtype: str | None = None,
                 min_magnitude: float | None = None,
                 max_magnitude: float | None = None,
                 saros_number: int | None = None,
                 visibility_region: str | None = None) -> EclipseListResponse:
    try:
        synchronize_catalog(db, eclipse_type, year)

        events = get_eclipse_events_from_db(db,eclipse_type,year)

        total_events = len(events)

        events = filter_eclipse_events(events=events,
                                       eclipse_subtype=eclipse_subtype,
                                       min_magnitude=min_magnitude,
                                       max_magnitude=max_magnitude,
                                       saros_number=saros_number,
                                       visibility_region=visibility_region)
    except HTTPException:
        raise

    except SQLAlchemyError as error:
        logger.exception("Database error while retrieving eclipses")
        raise HTTPException(status_code=500,
                            detail="Could not retrieve eclipse events") from error

    return EclipseListResponse(start_year=year,
                               end_year=year,
                               total_events=total_events,
                               events=events)
@router.get("/eclipses/solar", response_model=EclipseListResponse)
def get_solar_eclipses(year: int = Query(..., ge=2020, le=2050),
                      eclipse_subtype: str | None = Query(default=None),
                      min_magnitude: float | None = Query(default=None),
                      max_magnitude: float | None = Query(default=None),
                      saros_number: int | None = Query(default=None, ge=1),
                      visibility_region: str | None = Query(default=None),
                      db: Session = Depends(get_db)):
    return get_eclipses(db, "solar", year,
                        eclipse_subtype, min_magnitude, max_magnitude,
                        saros_number, visibility_region)

@router.get("/eclipses/lunar", response_model=EclipseListResponse)
def get_lunar_eclipses(year: int = Query(..., ge=2020, le=2050),
                       eclipse_subtype: str | None = Query(default=None),
                       min_magnitude: float | None = Query(default=None),
                       max_magnitude: float | None = Query(default=None),
                       saros_number: int | None = Query(default=None, ge=1),
                       visibility_region: str | None = Query(default=None),
                       db: Session = Depends(get_db)):
    return get_eclipses(db,"lunar", year,
                        eclipse_subtype, min_magnitude, max_magnitude,
                        saros_number, visibility_region)