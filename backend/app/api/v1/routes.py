import logging
from datetime import date
from fastapi import APIRouter, Query, HTTPException
from app.config import settings
from app.schemas import RouteSearchResponse, StationOut
from app.routes_calculator import SEED_STATIONS, calculate_routes, find_station_by_code, normalize_station_code
from app.yandex_client import yandex_client
from app.circuit_breaker import yandex_breaker
from app.redis_client import get_cached, set_cached

logger = logging.getLogger("transit.routes")
router = APIRouter(prefix="/routes", tags=["Routes"])

@router.get("/search", response_model=RouteSearchResponse)
async def search_routes(
    from_code: str = Query(..., description="Код станции отправления (напр. s9602497 или s9600370)"),
    to_code: str = Query(..., description="Код станции назначения (напр. s9602725 или s9603175)"),
    date_str: str = Query(str(date.today()), alias="date", description="Дата поездки в формате ГГГГ-ММ-ДД")
):
    st_from = find_station_by_code(from_code)
    st_to = find_station_by_code(to_code)

    if not st_from or not st_to:
        logger.warning(f"[404 NOT FOUND] Station lookup failed for from='{from_code}', to='{to_code}'")
        raise HTTPException(status_code=404, detail="Станция не найдена в реестре полигона")

    norm_from = normalize_station_code(from_code)
    norm_to = normalize_station_code(to_code)

    cache_key = f"routes:{norm_from}:{norm_to}:{date_str}"
    cached_routes = await get_cached(cache_key)

    is_degraded = yandex_breaker.is_degraded()

    if cached_routes:
        logger.info(f"[CACHE HIT] Key '{cache_key}' found in Redis. Returned {len(cached_routes)} routes instantly.")
        routes_data = cached_routes
    else:
        logger.info(f"[CACHE MISS] Key '{cache_key}' not in Redis. Initiating provider query / graph engine...")
        routes_data = None

        # 1. Попытка запроса в реальный API Яндекс.Расписаний
        if settings.YANDEX_API_KEY and not yandex_breaker.is_degraded():
            try:
                yandex_res = await yandex_client.get_search_schedule(norm_from, norm_to, date_str)
                if yandex_res and "segments" in yandex_res and len(yandex_res["segments"]) > 0:
                    routes_data = yandex_client.parse_yandex_response(yandex_res, norm_from, norm_to)
                    logger.info(f"[LIVE YANDEX RASP] Successfully retrieved {len(routes_data)} live suburban trains.")
            except Exception as e:
                logger.error(f"[YANDEX INTEGRATION EXCEPTION] {e}")
                is_degraded = True

        # 2. Если API недоступен, квота исчерпана или поездов нет - Graceful Degradation на локальный граф
        if not routes_data:
            if settings.YANDEX_API_KEY:
                is_degraded = True
                logger.warning(f"[FALLBACK GRAPH] Switched to offline graph engine for {norm_from} -> {norm_to}")
            routes_data = calculate_routes(norm_from, norm_to)

        logger.info(f"[CACHE STORE] Stored {len(routes_data)} routes in Redis with TTL=300s.")
        await set_cached(cache_key, routes_data, ttl_seconds=300)

    system_status = "DEGRADED_OFFLINE" if is_degraded else "OPERATIONAL"

    return RouteSearchResponse(
        from_station=StationOut(**st_from),
        to_station=StationOut(**st_to),
        search_date=date_str,
        is_degraded=is_degraded,
        system_status=system_status,
        routes_count=len(routes_data),
        routes=routes_data
    )
