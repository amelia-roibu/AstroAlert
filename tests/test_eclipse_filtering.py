from datetime import date, time

from app.schemas.eclipse import EclipseEvent
from app.services.filtering import filter_eclipse_events


def sample_events():
    return [
        EclipseEvent(
            id="1",
            name="Total Solar Eclipse",
            event_date=date(2024, 4, 8),
            source="NASA",
            eclipse_type="solar",
            eclipse_subtype="total",
            greatest_eclipse_td=time(18, 18, 29),
            magnitude=1.057,
            saros_number=139,
            duration="04m28s",
            visibility_regions="N. America"
        ),
        EclipseEvent(
            id="2",
            name="Annular Solar Eclipse",
            event_date=date(2024, 10, 2),
            source="NASA",
            eclipse_type="solar",
            eclipse_subtype="annular",
            greatest_eclipse_td=time(18, 45),
            magnitude=0.932,
            saros_number=144,
            duration="07m25s",
            visibility_regions="Pacific, S. America"
        )
    ]


def test_filter_by_subtype():
    result = filter_eclipse_events(sample_events(), eclipse_subtype="TOTAL")
    assert len(result) == 1
    assert result[0].eclipse_subtype == "total"


def test_filter_by_magnitude():
    result = filter_eclipse_events(sample_events(), min_magnitude=1.0)
    assert len(result) == 1
    assert result[0].magnitude == 1.057


def test_filter_by_saros_number():
    result = filter_eclipse_events(sample_events(), saros_number=144)
    assert len(result) == 1
    assert result[0].saros_number == 144


def test_filter_by_visibility_region():
    result = filter_eclipse_events(sample_events(), visibility_region="america")
    assert len(result) == 2


def test_combined_filters():
    result = filter_eclipse_events(
        sample_events(),
        eclipse_subtype="total",
        min_magnitude=1.0,
        saros_number=139,
        visibility_region="America"
    )
    assert len(result) == 1


def test_no_filters():
    events = sample_events()
    result = filter_eclipse_events(events)
    assert len(result) == len(events)