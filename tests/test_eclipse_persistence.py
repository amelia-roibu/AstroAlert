
from datetime import date, time

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base
from app.models import AstronomicalEvent, EclipseDetail
from app.schemas.eclipse import EclipseEvent
from app.services.persistence import persist_eclipse_events


@pytest.fixture
def db_session(tmp_path):
    # Cream o baza de date temporara pentru fiecare test.
    database_file = tmp_path / "test_eclipses.db"
    test_engine = create_engine(f"sqlite:///{database_file}")

    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    db = TestingSessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def sample_eclipses():
    return [
        EclipseEvent(
            id="NASA-SOLAR-2024-04-08",
            name="Total Solar Eclipse of 2024 Apr 08",
            event_date=date(2024, 4, 8),
            source="NASA",
            eclipse_type="solar",
            eclipse_subtype="total",
            greatest_eclipse_td=time(18, 17, 15),
            magnitude=1.056,
            saros_number=139,
            duration="4m 28s",
            visibility_regions="North America",
        ),
        EclipseEvent(
            id="NASA-LUNAR-2024-03-25",
            name="Penumbral Lunar Eclipse of 2024 Mar 25",
            event_date=date(2024, 3, 25),
            source="NASA",
            eclipse_type="lunar",
            eclipse_subtype="penumbral",
            greatest_eclipse_td=time(7, 12, 0),
            magnitude=-0.132,
            saros_number=113,
            duration=None,
            visibility_regions="Europe, Africa, Asia",
        ),
    ]


def test_insert_eclipse_events(db_session, sample_eclipses):
    processed = persist_eclipse_events(db_session, sample_eclipses)

    assert processed == 2

    assert db_session.query(AstronomicalEvent).count() == 2
    assert db_session.query(EclipseDetail).count() == 2

    solar_event = (
        db_session.query(AstronomicalEvent)
        .filter_by(external_id=sample_eclipses[0].id)
        .one()
    )

    solar_detail = (
        db_session.query(EclipseDetail)
        .filter_by(event_id=solar_event.id)
        .one()
    )

    assert solar_event.event_type == "SOLAR_ECLIPSE"
    assert solar_detail.eclipse_type == "solar"
    assert solar_detail.eclipse_subtype == "total"
    assert solar_detail.saros_number == 139


def test_update_existing_eclipse_events(db_session, sample_eclipses):
    # Salvam initial eclipsele.
    persist_eclipse_events(db_session, sample_eclipses)

    # Modificam cateva valori ale primei eclipse.
    sample_eclipses[0].name = "Updated Solar Eclipse"
    sample_eclipses[0].magnitude = 1.1
    sample_eclipses[0].duration = "4m 30s"

    # Procesam din nou aceleasi eclipse.
    processed = persist_eclipse_events(db_session, sample_eclipses)

    assert processed == 2

    # Nu trebuie sa apara duplicate.
    assert db_session.query(AstronomicalEvent).count() == 2
    assert db_session.query(EclipseDetail).count() == 2

    event = (
        db_session.query(AstronomicalEvent)
        .filter_by(external_id=sample_eclipses[0].id)
        .one()
    )

    detail = (
        db_session.query(EclipseDetail)
        .filter_by(event_id=event.id)
        .one()
    )

    assert event.name == "Updated Solar Eclipse"
    assert detail.magnitude == 1.1
    assert detail.duration == "4m 30s"


def test_persist_empty_eclipse_list(db_session):
    processed = persist_eclipse_events(db_session, [])

    assert processed == 0
    assert db_session.query(AstronomicalEvent).count() == 0
    assert db_session.query(EclipseDetail).count() == 0


def test_rollback_on_error(db_session, sample_eclipses, monkeypatch):
    # Simulam o eroare la confirmarea tranzactiei.
    def failing_commit():
        raise RuntimeError("Simulated database error")

    monkeypatch.setattr(db_session, "commit", failing_commit)

    with pytest.raises(RuntimeError, match="Simulated database error"):
        persist_eclipse_events(db_session, sample_eclipses)

    # Verificam daca modificarile au fost anulate.
    assert db_session.query(AstronomicalEvent).count() == 0
    assert db_session.query(EclipseDetail).count() == 0
