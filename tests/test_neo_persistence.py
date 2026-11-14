from datetime import date
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base
from app.models import Asteroid, AstronomicalEvent, NeoApproach
from app.schemas.neo import NeoEvent
from app.services.persistence import persist_neo_events

@pytest.fixture
def db_session(tmp_path):
    # cream o baza de date temporara pentru fiecare test
    database_file = tmp_path / "test_astroalert.db"
    test_engine = create_engine(f"sqlite:///{database_file}")

    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(bind=test_engine,
                                        autoflush=False,
                                        autocommit=False,)

    db = TestingSessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()

@pytest.fixture
def sample_events():
    return [
        NeoEvent(id="12345",
                external_id="12345:1794564000000",
                name="Asteroid Alpha",
                event_date=date(2026, 11, 10),
                source="NASA NeoWs",
                close_approach_date=date(2026, 11, 10),
                is_potentially_hazardous=True,
                estimated_diameter_km=0.5,
                miss_distance_km=5_000_000,
                relative_velocity_km_h=30_000,
                orbiting_body="Earth",),
        NeoEvent(id="12345",
                external_id="12345:1794567600000",
                name="Asteroid Alpha",
                event_date=date(2026, 11, 10),
                source="NASA NeoWs",
                close_approach_date=date(2026, 11, 10),
                is_potentially_hazardous=True,
                estimated_diameter_km=0.5,
                miss_distance_km=7_000_000,
                relative_velocity_km_h=28_000,
                orbiting_body="Earth",),]

def test_insert_neo_events(db_session, sample_events):
    processed = persist_neo_events(db_session, sample_events)

    assert processed == 2

    assert db_session.query(Asteroid).count() == 1
    assert db_session.query(AstronomicalEvent).count() == 2
    assert db_session.query(NeoApproach).count() == 2

    asteroid = db_session.query(Asteroid).one()

    assert len(asteroid.approaches) == 2

def test_update_existing_neo_events(db_session, sample_events):
    # prima salvare
    persist_neo_events(db_session, sample_events)

    # modificam datele primei apropieri
    sample_events[0].miss_distance_km = 4_000_000
    sample_events[0].relative_velocity_km_h = 32_000

    # procesam din nou aceleasi evenimente
    persist_neo_events(db_session, sample_events)

    # nu trebuie sa apara duplicate
    assert db_session.query(Asteroid).count() == 1
    assert db_session.query(AstronomicalEvent).count() == 2
    assert db_session.query(NeoApproach).count() == 2

    # verificam daca valorile au fost actualizate
    approach = (db_session.query(NeoApproach)
                .join(AstronomicalEvent)
                .filter(AstronomicalEvent.external_id == sample_events[0].external_id)
                .one())

    assert approach.miss_distance_km == 4_000_000
    assert approach.relative_velocity_km_h == 32_000

def test_rollback_on_error(db_session, sample_events, monkeypatch):
    # simulam o eroare la confirmarea tranzactiei
    def failing_commit():
        raise RuntimeError("Simulated database error")

    monkeypatch.setattr(db_session, "commit", failing_commit)

    with pytest.raises(RuntimeError, match="Simulated database error"):
        persist_neo_events(db_session, sample_events)

    # verificam daca modificarile au fost anulate
    assert db_session.query(Asteroid).count() == 0
    assert db_session.query(AstronomicalEvent).count() == 0
    assert db_session.query(NeoApproach).count() == 0