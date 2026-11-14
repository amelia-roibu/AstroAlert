# aici avem external API integration si data transformation
# adica se ocupa de comunicarea cu NASA si transformarea raspunsului

from datetime import date

from app.schemas.neo import NeoEvent

def normalize_neo_feed(nasa_data: dict) -> list[NeoEvent]:
    normalized_events = []
    near_earth_objects = nasa_data.get("near_earth_objects", {})
    for approach_date, asteroids in near_earth_objects.items():
        for asteroid in asteroids:
            close_approaches = asteroid.get("close_approach_data", [])
            matching_approaches = [item for item in close_approaches if item.get("close_approach_date") == approach_date]

            diameter = asteroid["estimated_diameter"]["kilometers"]

            for approach in matching_approaches:
                miss_distance = approach["miss_distance"]
                velocity = approach["relative_velocity"]
                epoch = approach["epoch_date_close_approach"]

                event = NeoEvent(id=str(asteroid["id"]),
                                    external_id=f'{asteroid["id"]}:{epoch}',
                                    name=asteroid["name"],
                                    event_date=date.fromisoformat(approach_date),
                                    source="NASA NeoWs",
                                    close_approach_date=date.fromisoformat(approach_date),
                                    is_potentially_hazardous=asteroid["is_potentially_hazardous_asteroid"],
                                    estimated_diameter_km=float(diameter["estimated_diameter_max"]),
                                    miss_distance_km=float(miss_distance["kilometers"]),
                                    relative_velocity_km_h=float(velocity["kilometers_per_hour"]),
                                    orbiting_body=approach["orbiting_body"],)

                normalized_events.append(event)

    return normalized_events