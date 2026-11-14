from datetime import date

import pytest

from app.schemas.neo import NeoEvent
from app.services.filtering import filter_neo_events

@pytest.fixture
def sample_events():
    return [NeoEvent( id="1",
                    external_id="1:1794564000000",
                    name="Asteroid Alpha",
                    event_date=date(2026, 11, 10),
                    source="NASA NeoWs",
                    close_approach_date=date(2026, 11, 10),
                    is_potentially_hazardous=True,
                    estimated_diameter_km=0.5,
                    miss_distance_km=5_000_000,
                    relative_velocity_km_h=30_000,
                    orbiting_body="Earth"),
            NeoEvent( id="2",
                    external_id="2:1794567600000",
                    name="Asteroid Beta",
                    event_date=date(2026, 11, 10),
                    source="NASA NeoWs",
                    close_approach_date=date(2026, 11, 10),
                    is_potentially_hazardous=False,
                    estimated_diameter_km=0.2,
                    miss_distance_km=15_000_000,
                    relative_velocity_km_h=25_000,
                    orbiting_body="Earth") ]

def test_hazardous_filter(sample_events):
    result = filter_neo_events(sample_events, hazardous_only=True)

    assert len(result) == 1
    assert result[0].id == "1"

def test_max_distance_filter(sample_events):
    result = filter_neo_events(sample_events, max_distance_km=10_000_000)

    assert len(result) == 1
    assert result[0].id == "1"

def test_min_diameter_filter(sample_events):
    result = filter_neo_events(sample_events, min_diameter_km=0.3)

    assert len(result) == 1
    assert result[0].id == "1"

def test_min_velocity_filter(sample_events):
    result = filter_neo_events(sample_events, min_velocity_km_h=20_000)

    assert len(result) == 2

def test_combined_filters(sample_events):
    result = filter_neo_events(sample_events,
                               hazardous_only=True,
                               max_distance_km=10_000_000,
                               min_diameter_km=0.3,
                               min_velocity_km_h=25_000)

    assert len(result) == 1
    assert result[0].id == "1"

def test_empty_events():
    result = filter_neo_events([])

    assert result == []
    assert len(result) == 0

def test_no_filters(sample_events):
    result = filter_neo_events(sample_events)

    assert len(result) == 2
    assert result == sample_events

def test_values_at_limits(sample_events):
    result = filter_neo_events(sample_events,
                               max_distance_km=5_000_000,
                               min_diameter_km=0.5,
                               min_velocity_km_h=30_000)

    assert len(result) == 1
    assert result[0].id == "1"