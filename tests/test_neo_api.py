from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.connection import Base, get_db
from app.models import Asteroid, AstronomicalEvent, NeoApproach
import app.routers.neo as neo_router

@pytest.fixture
def api_test_environment(tmp_path, monkeypatch):
    # baza de date temporara, izolata de baza reala
    database_file = tmp_path / "test_api.db"
    test_engine = create_engine(f"sqlite:///{database_file}")

    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(bind=test_engine,
                                        autoflush=False,
                                        autocommit=False,)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # simulam existenta cheii API
    monkeypatch.setattr(neo_router, "NASA_API_KEY", "test-api-key")

    # raspuns NASA simulat
    nasa_data = {
        "near_earth_objects": {
            "2026-11-10": [
                {
                    "id": "12345",
                    "name": "Asteroid Alpha",
                    "is_potentially_hazardous_asteroid": True,
                    "estimated_diameter": {
                        "kilometers": {
                            "estimated_diameter_min": 0.3,
                            "estimated_diameter_max": 0.7,
                        }
                    },
                    "close_approach_data": [
                        {
                            "epoch_date_close_approach": 1794564000000,
                            "close_approach_date": "2026-11-10",
                            "miss_distance": {
                                "kilometers": "5000000"
                            },
                            "relative_velocity": {
                                "kilometers_per_hour": "30000"
                            },
                            "orbiting_body": "Earth",
                        }
                    ],
                }
            ]
        }
    }

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return nasa_data

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def get(self, *args, **kwargs):
            return FakeResponse()

    # inlocuim clientul HTTP real cu cel simulat
    monkeypatch.setattr(neo_router.httpx, "Client", FakeClient)

    client = TestClient(app)

    yield client, TestingSessionLocal

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()

def test_get_neo_endpoint_and_persist_data(api_test_environment):
    client, TestingSessionLocal = api_test_environment

    response = client.get("/api/neo?start_date=2026-11-10")

    # verificam răspunsul HTTP
    assert response.status_code == 200

    data = response.json()

    assert data["start_date"] == "2026-11-10"
    assert data["total_events"] == 1
    assert len(data["events"]) == 1

    assert data["events"][0]["name"] == "Asteroid Alpha"
    assert data["events"][0]["is_potentially_hazardous"] is True

    # verificam daca datele au ajuns in baza de date
    db = TestingSessionLocal()

    try:
        assert db.query(Asteroid).count() == 1
        assert db.query(AstronomicalEvent).count() == 1
        assert db.query(NeoApproach).count() == 1
    finally:
        db.close()