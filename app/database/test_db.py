from datetime import datetime
from uuid import uuid4
from app.database.connection import SessionLocal
from app.models import Asteroid, AstronomicalEvent, NeoApproach
from app.routers.neo import router


def test_database_relationship():
    test_id = str(uuid4())
    with SessionLocal() as db:
        # cream un asteroid
        asteroid = Asteroid(nasa_id=f"TEST-{test_id}",
                            name="AstroAlert test asteroid",
                            diameter_km=0.5,
                            is_potentially_hazardous=True,)
        #cream doua evenimente de apropiere
        for i in range(1,3):
            event = AstronomicalEvent(event_type="NEO",
                                      external_id=f"{test_id}-approach-{i}",
                                      name=f"Test approach {i}",
                                      source="AstroAlert test",
                                      start_date=datetime.now(),)
            approach = NeoApproach(event=event,
                                   asteroid=asteroid,
                                   miss_distance_km=1_000_000 * i,
                                   relative_velocity_km_h=25_000,
                                   orbiting_body="Earth",)

            db.add(approach)

        # salvam obiectele
        db.add(asteroid)
        db.commit()

        # citim asteroidul din bd
        saved_asteroid = (db.query(Asteroid)
                          .filter_by(nasa_id=f"TEST-{test_id}")
                          .first())

        print("\nAsteroid:", saved_asteroid.name)
        print("ID intern:", saved_asteroid.id)
        print("Numar apropieri:", len(saved_asteroid.approaches))

        for approach in saved_asteroid.approaches:
            print(f"Eveniment: {approach.event.name} | "
                  f"Distanta: {approach.miss_distance_km} km")

if __name__ == "__main__":
    test_database_relationship()