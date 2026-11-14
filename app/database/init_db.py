from app.database.connection import Base, engine
from app.models import Asteroid, AstronomicalEvent, NeoApproach

def create_tables():
    # contine informatiile despre toate tabelele declarate prin clasele SQLAlchemy
    Base.metadata.create_all(bind=engine)
    print("AstroAlert database tables created successfully")

if __name__ == "__main__":
    create_tables()