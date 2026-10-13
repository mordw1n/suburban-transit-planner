from typing import List, Optional
from pydantic import BaseModel

class StationOut(BaseModel):
    id: str
    code_yandex: str
    title: str
    direction: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_junction: bool

    class Config:
        from_attributes = True

class TrainOut(BaseModel):
    train_number: str
    train_type: str
    carrier: str

class RouteSegmentOut(BaseModel):
    train_number: str
    train_type: str
    station_from_title: str
    station_from_code: str
    station_to_title: str
    station_to_code: str
    departure_time: str
    arrival_time: str
    delay_minutes: int = 0
    status: str = "ON_TIME"

class TransferInfoOut(BaseModel):
    junction_station_title: str
    junction_station_code: str
    wait_time_minutes: int
    walking_buffer_minutes: int = 7
    is_tight_connection: bool = False

class RouteOptionOut(BaseModel):
    option_id: str
    is_direct: bool
    total_duration_minutes: int
    departure_time: str
    arrival_time: str
    segments: List[RouteSegmentOut]
    transfer: Optional[TransferInfoOut] = None

class RouteSearchResponse(BaseModel):
    from_station: StationOut
    to_station: StationOut
    search_date: str
    is_degraded: bool = False
    system_status: str = "OPERATIONAL"
    routes_count: int
    routes: List[RouteOptionOut]

class LiveDelayItemOut(BaseModel):
    train_number: str
    station_title: str
    scheduled_time: str
    delay_minutes: int
    status: str
    recorded_at: str

class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: str
    timestamp: str
