from typing import List
from datetime import datetime
from fastapi import APIRouter
from app.schemas import LiveDelayItemOut

router = APIRouter(prefix="/delays", tags=["Delays"])

@router.get("/live", response_model=List[LiveDelayItemOut])
async def list_live_delays():
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    return [
        LiveDelayItemOut(
            train_number="6127 Стандарт",
            station_title="Зеленогорск",
            scheduled_time="09:50",
            delay_minutes=5,
            status="DELAYED",
            recorded_at=now_str
        ),
        LiveDelayItemOut(
            train_number="6533 Стандарт",
            station_title="Девяткино",
            scheduled_time="09:45",
            delay_minutes=12,
            status="DELAYED",
            recorded_at=now_str
        ),
        LiveDelayItemOut(
            train_number="6101 Отмененный",
            station_title="Финляндский вокзал",
            scheduled_time="11:00",
            delay_minutes=0,
            status="CANCELLED",
            recorded_at=now_str
        )
    ]
