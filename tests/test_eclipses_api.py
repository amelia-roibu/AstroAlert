import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base, get_db
from app.models import EclipseSync, AstronomicalEvent
from fastapi.testclient import TestClient
from app.main import app
import app.routers.eclipses as eclipses_router

client = TestClient(app)

@pytest.fixture
def isolated_db(tmp_path):
    database_file = tmp_path / "test_eclipses_api.db"
    engine = create_engine(f"sqlite:///{database_file}")

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestingSessionLocal

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

def test_get_solar_eclipses_success(monkeypatch):
    nasa_html = """
    <html>
    <body>
    <table>
        <tr><td colspan="7">Solar Eclipses: 2021 - 2030</td></tr>
        <tr>
            <td>Calendar Date</td>
            <td>TD of Greatest Eclipse</td>
            <td>Eclipse Type</td>
            <td>Saros Series</td>
            <td>Eclipse Magnitude</td>
            <td>Central Duration</td>
            <td>Geographic Region of Eclipse Visibility</td>
        </tr>
        <tr>
            <td>(Link to Global Map)</td>
            <td>(Link to Animation)</td>
            <td>(Link to Google Map)</td>
            <td>(Link to Saros)</td>
            <td></td>
            <td>(Link to Path Table)</td>
            <td></td>
        </tr>
        <tr>
            <td>2024 Apr 08</td>
            <td>18:18:29</td>
            <td>Total</td>
            <td>139</td>
            <td>1.057</td>
            <td>04m28s</td>
            <td>N. America</td>
        </tr>
        <tr>
            <td>2024 Oct 02</td>
            <td>18:45:00</td>
            <td>Annular</td>
            <td>144</td>
            <td>0.932</td>
            <td>07m25s</td>
            <td>Pacific, S. America</td>
        </tr>
    </table>
    </body>
    </html>
    """

    class MockResponse:
        text = nasa_html

        def raise_for_status(self):
            pass

    class MockClient:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def get(self, *args, **kwargs):
            return MockResponse()

    monkeypatch.setattr(
        eclipses_router.httpx,
        "Client",
        lambda **kwargs: MockClient()
    )

    response = client.get("/api/eclipses/solar?year=2024")

    assert response.status_code == 200

    data = response.json()

    assert data["total_events"] == 2
    assert data["start_year"] == 2024
    assert data["end_year"] == 2024
    assert data["events"][0]["eclipse_subtype"] == "total"
    assert data["events"][1]["eclipse_subtype"] == "annular"


def test_get_lunar_eclipses_success(monkeypatch):
    nasa_html = """
    <html>
    <body>
    <table>
        <tr><td colspan="7">Lunar Eclipses: 2021 - 2030</td></tr>
        <tr>
            <td>Calendar Date</td>
            <td>TD of Greatest Eclipse</td>
            <td>Eclipse Type</td>
            <td>Saros Series</td>
            <td>Umbral Magnitude</td>
            <td>Eclipse Duration</td>
            <td>Geographic Region of Eclipse Visibility</td>
        </tr>
        <tr>
            <td>2024 Mar 25</td>
            <td>07:13:59</td>
            <td>Penumbral</td>
            <td>113</td>
            <td>-0.132</td>
            <td>-</td>
            <td>Americas</td>
        </tr>
    </table>
    </body>
    </html>
    """

    class MockResponse:
        text = nasa_html

        def raise_for_status(self):
            pass

    class MockClient:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def get(self, *args, **kwargs):
            return MockResponse()

    monkeypatch.setattr(
        eclipses_router.httpx,
        "Client",
        lambda **kwargs: MockClient()
    )

    response = client.get("/api/eclipses/lunar?year=2024")

    assert response.status_code == 200

    data = response.json()

    assert data["total_events"] == 1
    assert data["events"][0]["eclipse_subtype"] == "penumbral"
    assert data["events"][0]["magnitude"] == -0.132
    assert data["events"][0]["duration"] is None


def test_get_solar_eclipses_invalid_year():
    response = client.get("/api/eclipses/solar?year=2051")
    assert response.status_code == 422


def test_get_lunar_eclipses_invalid_year():
    response = client.get("/api/eclipses/lunar?year=2019")
    assert response.status_code == 422


def test_catalog_is_downloaded_only_once(monkeypatch, isolated_db):
    calls = []

    def fake_fetch_catalog(eclipse_type, year):
        calls.append((eclipse_type, year))
        return []

    monkeypatch.setattr(
        eclipses_router,
        "fetch_catalog",
        fake_fetch_catalog
    )

    first_response = client.get("/api/eclipses/solar?year=2024")
    second_response = client.get("/api/eclipses/solar?year=2025")

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    # Ambii ani folosesc catalogul solar 2021-2030.
    assert calls == [("solar", 2024)]

    with isolated_db() as db:
        assert db.query(EclipseSync).count() == 1
        assert db.query(AstronomicalEvent).count() == 0


def test_solar_and_lunar_catalogs_sync_separately(
    monkeypatch,
    isolated_db
):
    calls = []

    def fake_fetch_catalog(eclipse_type, year):
        calls.append((eclipse_type, year))
        return []

    monkeypatch.setattr(
        eclipses_router,
        "fetch_catalog",
        fake_fetch_catalog
    )

    solar_response = client.get("/api/eclipses/solar?year=2024")
    lunar_response = client.get("/api/eclipses/lunar?year=2024")

    assert solar_response.status_code == 200
    assert lunar_response.status_code == 200

    assert calls == [
        ("solar", 2024),
        ("lunar", 2024),
    ]

    with isolated_db() as db:
        assert db.query(EclipseSync).count() == 2
