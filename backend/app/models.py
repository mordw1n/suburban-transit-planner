import uuid
from datetime import datetime, time, date
from sqlalchemy import Column, String, Boolean, Float, Integer, Time, Date, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Station(Base):
    __tablename__ = "stations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    code_yandex = Column(String(32), unique=True, nullable=False, index=True)
    title = Column(String(128), nullable=False)
    direction = Column(String(64), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_junction = Column(Boolean, default=False)

    __table_args__ = (
        Index("idx_stations_direction", "direction"),
    )

class Train(Base):
    __tablename__ = "trains"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    train_number = Column(String(32), unique=True, nullable=False)
    train_type = Column(String(64), default="Стандарт")
    carrier = Column(String(64), default="СЗППК")

class ScheduleItem(Base):
    __tablename__ = "schedule_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    train_id = Column(String(36), ForeignKey("trains.id"), nullable=False)
    station_from_id = Column(String(36), ForeignKey("stations.id"), nullable=False)
    station_to_id = Column(String(36), ForeignKey("stations.id"), nullable=False)
    departure_time = Column(Time, nullable=False)
    arrival_time = Column(Time, nullable=False)
    days_mask = Column(Integer, default=127)
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        Index("idx_schedules_lookup", "station_from_id", "station_to_id", "departure_time"),
    )

class DelaysHistory(Base):
    __tablename__ = "delays_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_item_id = Column(String(36), ForeignKey("schedule_items.id"), nullable=False)
    event_date = Column(Date, default=date.today)
    delay_minutes = Column(Integer, default=0)
    status = Column(String(32), default="ON_TIME")
    recorded_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_delays_date", "event_date", "schedule_item_id"),
    )
