from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./astroalert.db"

# componenta sqlalchemy care gestioneaza comunicarea cu baza de date
engine = create_engine(DATABASE_URL,
                       connect_args={"check_same_thread": False})

# sesiune = unitatea de lucru prin care interactionam cu baza de date
SessionLocal = sessionmaker(bind=engine,
                            autoflush=False,
                            autocommit=False)

class Base(DeclarativeBase):
    pass
# vom folosi aceeasi clasa Base pentru toate modelele AstroAlert

# sqlite nu activeaza automat verificarea cheilor straine in toate conexiunile
@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
# un cursor este un obiect folosit pentru a executa comenzi SQL si pentru a interactiona cu o baza de date printr-o conexiune

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()