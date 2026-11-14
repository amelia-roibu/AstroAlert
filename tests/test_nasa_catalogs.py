
import pytest

from app.routers.eclipses import fetch_catalog


@pytest.mark.parametrize(
    "eclipse_type, year",
    [
        ("solar", 2020),
        ("solar", 2021),
        ("solar", 2031),
        ("solar", 2041),
        ("lunar", 2020),
        ("lunar", 2021),
        ("lunar", 2031),
        ("lunar", 2041),
    ],
)
def test_nasa_catalog_returns_valid_events(eclipse_type, year):
    events = fetch_catalog(eclipse_type, year)

    assert isinstance(events, list)
    assert len(events) > 0

    for event in events:
        assert event["eclipse_type"] == eclipse_type
        decade_start = 2011 if year == 2020 else year
        decade_end = decade_start + 9

        assert decade_start <= event["event_date"].year <= decade_end
        assert event["source"] == "NASA"
        assert event["id"].startswith(f"NASA-{eclipse_type.upper()}-")
        assert event["name"]
        assert event["eclipse_subtype"]
        assert event["greatest_eclipse_td"] is not None
        assert isinstance(event["magnitude"], float)
        assert isinstance(event["saros_number"], int)

    ids = [event["id"] for event in events]
    assert len(ids) == len(set(ids))
