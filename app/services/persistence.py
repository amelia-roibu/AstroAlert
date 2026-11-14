# logica de salvare in baza de date, fara sa stie nimic
# despre cererile HTTP sau endpoint-uri

from datetime import time, datetime
from sqlalchemy.orm import Session
from app.models import (Asteroid, AstronomicalEvent, NeoApproach, EclipseDetail, EclipseSync,)
from app.schemas.neo import NeoEvent
from app.schemas.eclipse import EclipseEvent

def persist_neo_events(db: Session, events: list[NeoEvent]) -> int:
    # salveaza sau updateaza Neo events in baza de date si returneaza
    # numarul de evenimente procesate
    if not events:
        return 0

    try:
        for neo_event in events:
            asteroid = (db.query(Asteroid)
                        .filter_by(nasa_id=neo_event.id)
                        .first())
            if asteroid is None:
                asteroid = Asteroid(nasa_id=neo_event.id,
                                    name=neo_event.name,
                                    diameter_km=neo_event.estimated_diameter_km,
                                    is_potentially_hazardous=neo_event.is_potentially_hazardous,)
                db.add(asteroid)

            else:
                asteroid.name = neo_event.name
                asteroid.diameter_km = neo_event.estimated_diameter_km
                asteroid.is_potentially_hazardous = neo_event.is_potentially_hazardous

            db.flush()

            astronomical_event = (db.query(AstronomicalEvent)
                                  .filter_by(source=neo_event.source,
                                             external_id=neo_event.external_id)
                                  .first())

            if astronomical_event is None:
                astronomical_event = AstronomicalEvent(event_type="NEO",
                                                        external_id=neo_event.external_id,
                                                        name=neo_event.name,
                                                        source=neo_event.source,
                                                        start_date=datetime.combine(neo_event.event_date, time.min),)
                db.add(astronomical_event)

            else:
                astronomical_event.name = neo_event.name
                astronomical_event.start_date = datetime.combine(neo_event.event_date, time.min)

            db.flush()

            neo_approach = (db.query(NeoApproach)
                            .filter_by(event_id=astronomical_event.id)
                            .first())

            if neo_approach is None:
                neo_approach = NeoApproach(event=astronomical_event,
                                            asteroid=asteroid,
                                            miss_distance_km=neo_event.miss_distance_km,
                                            relative_velocity_km_h=neo_event.relative_velocity_km_h,
                                            orbiting_body=neo_event.orbiting_body,)
                db.add(neo_approach)

            else:
                neo_approach.asteroid = asteroid
                neo_approach.miss_distance_km = neo_event.miss_distance_km
                neo_approach.relative_velocity_km_h = neo_event.relative_velocity_km_h
                neo_approach.orbiting_body = neo_event.orbiting_body

            db.flush()

        db.commit()
        return len(events)

    except Exception:
        db.rollback()
        raise


def persist_eclipse_events(db: Session, events: list[EclipseEvent]) -> int:
    # salveaza sau actualizeaza eclipsele in baza de date
    # si returneaza numarul de evenimente procesate
    if not events:
        return 0

    try:
        for eclipse in events:
            astronomical_event = (db.query(AstronomicalEvent)
                                    .filter_by(
                                        source=eclipse.source,
                                        external_id=eclipse.id)
                                    .first())
            if astronomical_event is None:
                astronomical_event = AstronomicalEvent(event_type=f"{eclipse.eclipse_type.upper()}_ECLIPSE",
                                                        external_id=eclipse.id,
                                                        name=eclipse.name,
                                                        source=eclipse.source,
                                                        start_date=datetime.combine(
                                                            eclipse.event_date,
                                                            time.min),)
                db.add(astronomical_event)

            else:
                astronomical_event.event_type = f"{eclipse.eclipse_type.upper()}_ECLIPSE"
                astronomical_event.name = eclipse.name
                astronomical_event.start_date = datetime.combine(eclipse.event_date,time.min)

            db.flush()

            eclipse_detail = (db.query(EclipseDetail)
                            .filter_by(event_id=astronomical_event.id)
                            .first())

            if eclipse_detail is None:
                eclipse_detail = EclipseDetail(event_id=astronomical_event.id,
                                                eclipse_type=eclipse.eclipse_type,
                                                eclipse_subtype=eclipse.eclipse_subtype,
                                                greatest_eclipse_td=eclipse.greatest_eclipse_td,
                                                magnitude=eclipse.magnitude,
                                                saros_number=eclipse.saros_number,
                                                duration=eclipse.duration,
                                                visibility_regions=eclipse.visibility_regions,)
                db.add(eclipse_detail)

            else:
                eclipse_detail.eclipse_type = eclipse.eclipse_type
                eclipse_detail.eclipse_subtype = eclipse.eclipse_subtype
                eclipse_detail.greatest_eclipse_td = eclipse.greatest_eclipse_td
                eclipse_detail.magnitude = eclipse.magnitude
                eclipse_detail.saros_number = eclipse.saros_number
                eclipse_detail.duration = eclipse.duration
                eclipse_detail.visibility_regions = eclipse.visibility_regions

            db.flush()

        db.commit()
        return len(events)

    except Exception:
        db.rollback()
        raise


def is_eclipse_catalog_synced(db: Session, eclipse_type: str, catalog_decade: int) -> bool:
    return (db.query(EclipseSync)
            .filter_by(eclipse_type=eclipse_type,
                       catalog_decade=catalog_decade)
            .first()
            is not None )

def mark_eclipse_catalog_synced(db: Session, eclipse_type: str, catalog_decade: int) -> None:
    try:
        synchronization = EclipseSync(eclipse_type=eclipse_type,
                                      catalog_decade=catalog_decade)
        db.add(synchronization)
        db.commit()

    except Exception:
        db.rollback()
        raise

def get_eclipse_events_from_db(db: Session, eclipse_type: str, year: int) -> list[EclipseEvent]:
    results = (db.query(AstronomicalEvent, EclipseDetail)
                .join(EclipseDetail,
                      AstronomicalEvent.id == EclipseDetail.event_id)
                .filter(AstronomicalEvent.event_type == f"{eclipse_type.upper()}_ECLIPSE",
                                 AstronomicalEvent.start_date >= datetime(year, 1, 1),
                                 AstronomicalEvent.start_date < datetime(year + 1, 1, 1))
                .order_by(AstronomicalEvent.start_date)
                .all())

    return [EclipseEvent(id=event.external_id,
                        name=event.name,
                        event_date=event.start_date.date(),
                        source=event.source,
                        eclipse_type=detail.eclipse_type,
                        eclipse_subtype=detail.eclipse_subtype,
                        greatest_eclipse_td=detail.greatest_eclipse_td,
                        magnitude=detail.magnitude,
                        saros_number=detail.saros_number,
                        duration=detail.duration,
                        visibility_regions=detail.visibility_regions)
        for event, detail in results]
