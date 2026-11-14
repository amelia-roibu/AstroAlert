import pytest
from datetime import date
from app.services.nasa import normalize_neo_feed

@pytest.fixture
def sample_data():
    return {
        "near_earth_objects": {
            "2026-11-13": [
                {
                    "id": "12345",
                    "name": "Test Asteroid",
                    "is_potentially_hazardous_asteroid": False,
                    "estimated_diameter": {
                        "kilometers": {"estimated_diameter_max": 0.5}
                    },
                    "close_approach_data": [
                        {
                            "epoch_date_close_approach": "1794564000000",
                            "close_approach_date": "2026-11-13",
                            "miss_distance": {"kilometers": "1000000"},
                            "relative_velocity": {"kilometers_per_hour": "25000"},
                            "orbiting_body": "Earth"
                        },
                        {
                            "epoch_date_close_approach": "1794567600000",
                            "close_approach_date": "2026-11-13",
                            "miss_distance": {"kilometers": "1200000"},
                            "relative_velocity": {"kilometers_per_hour": "26000"},
                            "orbiting_body": "Earth"
                        },
                        {
                            "epoch_date_close_approach": "1794650400000",
                            "close_approach_date": "2026-11-14",
                            "miss_distance": {"kilometers": "1500000"},
                            "relative_velocity": {"kilometers_per_hour": "27000"},
                            "orbiting_body": "Earth"
                        }
                    ]
                }
            ]
        }
    }

def test_normalize_neo_feed(sample_data):
    events = normalize_neo_feed(sample_data)

    assert len(events) == 2
    event = events[0]
    assert event.id == "12345"
    assert event.name == "Test Asteroid"
    assert event.event_date == date(2026, 11, 13)
    assert event.close_approach_date == date(2026, 11, 13)
    assert event.source == "NASA NeoWs"
    assert event.is_potentially_hazardous is False
    assert event.estimated_diameter_km == 0.5
    assert event.miss_distance_km == 1_000_000
    assert event.relative_velocity_km_h == 25_000
    assert event.orbiting_body == "Earth"

def test_normalize_multiple_approaches_on_the_same_date(sample_data):
    events = normalize_neo_feed(sample_data)
    assert len(events) == 2
    assert events[0].miss_distance_km == 1_000_000
    assert events[1].miss_distance_km == 1_200_000
    assert all(event.close_approach_date == date(2026, 11, 13) for event in events)

def test_normalize_empty_feed():
    nasa_data = {"near_earth_objects": {}}

    events = normalize_neo_feed(nasa_data)
    assert events == []