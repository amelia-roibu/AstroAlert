from datetime import datetime, time

from sqlalchemy import (Boolean, DateTime, Float, ForeignKey, Integer, String, Time, UniqueConstraint, func,)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base


class Asteroid(Base):
    __tablename__ = "asteroids"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nasa_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    diameter_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_potentially_hazardous: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    approaches: Mapped[list["NeoApproach"]] = relationship(back_populates="asteroid")

class AstronomicalEvent(Base):
    __tablename__ = "astronomical_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    external_id: Mapped[str | None] = mapped_column(String(150), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(100))
    start_date: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    neo_approach: Mapped["NeoApproach | None"] = relationship(back_populates="event", uselist=False,)

    eclipse_detail: Mapped["EclipseDetail | None"] = relationship(back_populates="event", uselist=False,)

    __table_args__ = (UniqueConstraint("source", "external_id", name="uq_event_source_external_id"),)


class NeoApproach(Base):
    __tablename__ = "neo_approaches"

    event_id: Mapped[int] = mapped_column(ForeignKey("astronomical_events.id"), primary_key=True,)
    asteroid_id: Mapped[int] = mapped_column(ForeignKey("asteroids.id"), index=True,)

    miss_distance_km: Mapped[float] = mapped_column(Float)
    relative_velocity_km_h: Mapped[float] = mapped_column(Float)
    orbiting_body: Mapped[str] = mapped_column(String(50))

    event: Mapped["AstronomicalEvent"] = relationship(back_populates="neo_approach")
    asteroid: Mapped["Asteroid"] = relationship(back_populates="approaches")



class EclipseDetail(Base):
    __tablename__ = "eclipse_details"

    event_id: Mapped[int] = mapped_column(ForeignKey("astronomical_events.id"), primary_key=True,)

    eclipse_type: Mapped[str] = mapped_column(String(20))
    eclipse_subtype: Mapped[str] = mapped_column(String(30))

    greatest_eclipse_td: Mapped[time | None] = mapped_column(Time, nullable=True, )

    magnitude: Mapped[float | None] = mapped_column(Float,nullable=True,)

    saros_number: Mapped[int | None] = mapped_column(Integer,nullable=True,)

    duration: Mapped[str | None] = mapped_column(String(50),nullable=True)

    visibility_regions: Mapped[str | None] = mapped_column(String(500),nullable=True,)

    event: Mapped["AstronomicalEvent"] = relationship(back_populates="eclipse_detail",)

class EclipseSync(Base):
    __tablename__ = "eclipse_syncs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    eclipse_type: Mapped[str] = mapped_column(String(20))
    catalog_decade: Mapped[int] = mapped_column(Integer)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "eclipse_type",
            "catalog_decade",
            name="uq_eclipse_sync_type_decade",
        ),
    )