# se ocupa de selectarea evenimentelor relevante

from app.schemas.neo import NeoEvent
from app.schemas.eclipse import EclipseEvent

def filter_neo_events(events: list[NeoEvent],
                      hazardous_only: bool = False,
                      max_distance_km: float | None = None,
                      min_diameter_km: float | None = None,
                      min_velocity_km_h: float | None = None) -> list[NeoEvent]:

    filtered_events = events.copy()

    if hazardous_only:
        filtered_events = [event for event in filtered_events if event.is_potentially_hazardous]

    if max_distance_km is not None:
        filtered_events = [event for event in filtered_events if event.miss_distance_km <= max_distance_km]

    if min_diameter_km is not None:
        filtered_events = [event for event in filtered_events if event.estimated_diameter_km >= min_diameter_km]

    if min_velocity_km_h is not None:
        filtered_events = [event for event in filtered_events if event.relative_velocity_km_h >= min_velocity_km_h]

    return filtered_events

def filter_eclipse_events(events: list[EclipseEvent],
                          eclipse_subtype: str | None = None,
                          min_magnitude: float | None = None,
                          max_magnitude: float | None = None,
                          saros_number: int | None = None,
                          visibility_region: str | None = None) -> list[EclipseEvent]:
    filtered_events = events.copy()

    if eclipse_subtype is not None:
        filtered_events = [event for event in filtered_events if event.eclipse_subtype.lower() == eclipse_subtype.lower()]

    if min_magnitude is not None:
        filtered_events = [event for event in filtered_events if event.magnitude is not None and event.magnitude >= min_magnitude]

    if max_magnitude is not None:
        filtered_events = [event for event in filtered_events if event.magnitude is not None and event.magnitude <= max_magnitude]

    if saros_number is not None:
        filtered_events = [event for event in filtered_events if event.saros_number == saros_number]

    if visibility_region is not None:
        filtered_events = [event for event in filtered_events if event.visibility_regions is not None and visibility_region.lower() in event.visibility_regions.lower()]

    return filtered_events