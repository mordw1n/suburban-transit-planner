from datetime import date
from fastapi import APIRouter, Query, HTTPException
from app.schemas import RouteSearchResponse, StationOut
from app.routes_calculator import SEED_STATIONS, calculate_routes
from app.circuit_breaker import yandex_breaker
from app.redis_client import get_cached, set_cached

router = APIRouter(prefix="/routes", tags=["Routes"])

@router.get("/search", response_model=RouteSearchResponse)
async def search_routes(
    from_code: str = Query(...),
    to_code: str = Query(...),
    date_str: str = Query(str(date.today()), alias="date")
):
    st_from = next((s for s in SEED_STATIONS if s["code_yandex"] == from_code), None)
    st_to = next((s for s in SEED_STATIONS if s["code_yandex"] == to_code), None)

    if not st_from or not st_to:
        raise HTTPException(status_code=404, detail="Станция не найдена")

    cache_key = f"routes:{from_code}:{to_code}:{date_str}"
    cached_routes = await get_cached(cache_key)

    is_degraded = yandex_breaker.is_degraded()
    system_status = "DEGRADED_OFFLINE" if is_degraded else "OPERATIONAL"

    if cached_routes:
        routes_data = cached_routes
    else:
        routes_data = calculate_routes(from_code, to_code)
        await set_cached(cache_key, routes_data, ttl_seconds=300)

    return RouteSearchResponse(
        from_station=StationOut(**st_from),
        to_station=StationOut(**st_to),
        search_date=date_str,
        is_degraded=is_degraded,
        system_status=system_status,
        routes_count=len(routes_data),
        routes=routes_data
    )
