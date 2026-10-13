from typing import List, Optional
from fastapi import APIRouter, Query
from app.schemas import StationOut
from app.routes_calculator import SEED_STATIONS

router = APIRouter(prefix="/stations", tags=["Stations"])

@router.get("", response_model=List[StationOut])
async def list_stations(direction: Optional[str] = Query(None)):
    if direction:
        return [s for s in SEED_STATIONS if s["direction"].lower() == direction.lower()]
    return SEED_STATIONS
