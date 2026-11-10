import logging
import httpx
from typing import Dict, Any, Optional, List
from app.config import settings
from app.circuit_breaker import yandex_breaker

logger = logging.getLogger("transit.yandex_client")

class YandexSchedulesClient:
    def __init__(self):
        self.api_key = settings.YANDEX_API_KEY
        self.base_url = settings.YANDEX_API_BASE_URL

    async def get_search_schedule(self, from_code: str, to_code: str, date_str: str) -> Optional[Dict[str, Any]]:
        """
        Запрашивает расписание между двумя станциями через API Яндекс.Расписаний.
        Защищено паттерном Circuit Breaker: при сбоях предотвращает каскадные отказы.
        """
        if not yandex_breaker.can_execute():
            logger.warning("[CIRCUIT BREAKER: OPEN] External Yandex API is tripped. Skipping network call.")
            return None

        if not self.api_key:
            logger.info("Yandex API key is not configured. Using local calculation engine.")
            return None

        url = f"{self.base_url}/search/"
        params = {
            "apikey": self.api_key,
            "format": "json",
            "from": from_code,
            "to": to_code,
            "date": date_str,
            "transport_types": "suburban"
        }

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    yandex_breaker.record_success()
                    logger.info(f"[YANDEX API 200 OK] Received schedule response for {from_code} -> {to_code}")
                    return response.json()
                elif response.status_code == 429:
                    logger.error("[YANDEX API 429] Rate limit exceeded (500 req/day quota reached). Recording circuit breaker failure.")
                    yandex_breaker.record_failure()
                elif response.status_code in [500, 502, 503, 504]:
                    logger.error(f"[YANDEX API {response.status_code}] Upstream server error. Recording circuit breaker failure.")
                    yandex_breaker.record_failure()
                else:
                    logger.warning(f"[YANDEX API {response.status_code}] Unexpected HTTP status: {response.text[:200]}")
        except httpx.TimeoutException:
            logger.error("[YANDEX API TIMEOUT] Request timed out after 4.0s. Recording circuit breaker failure.")
            yandex_breaker.record_failure()
        except Exception as e:
            logger.error(f"[YANDEX API NETWORK ERROR] {e}. Recording circuit breaker failure.")
            yandex_breaker.record_failure()

        return None

    def parse_yandex_response(self, raw_json: Dict[str, Any], from_code: str, to_code: str) -> List[Dict[str, Any]]:
        """
        Преобразует ответ API Яндекс.Расписаний в унифицированный формат RouteOptionOut.
        """
        routes: List[Dict[str, Any]] = []
        segments = raw_json.get("segments", [])

        for idx, seg in enumerate(segments):
            thread = seg.get("thread", {})
            number = thread.get("number", f"sub-{idx+1}")
            title = thread.get("title", "")
            express_type = thread.get("express_type")

            if express_type == "express" or "Ласточка" in title:
                train_type = "Ласточка (Экспресс)"
            else:
                train_type = "Стандартная электричка"

            st_from = seg.get("from", {})
            st_to = seg.get("to", {})

            from_title = st_from.get("title") or st_from.get("popular_title") or from_code
            to_title = st_to.get("title") or st_to.get("popular_title") or to_code

            dep_raw = seg.get("departure", "")
            arr_raw = seg.get("arrival", "")

            # Извлечение HH:MM из '05:35:00' или '2026-11-16T05:35:00+03:00'
            dep_time = self._extract_hhmm(dep_raw)
            arr_time = self._extract_hhmm(arr_raw)

            # Вычисление продолжительности поездки
            duration_sec = seg.get("duration")
            if duration_sec:
                duration_min = int(duration_sec // 60)
            else:
                duration_min = self._diff_minutes(dep_time, arr_time)

            carrier_info = thread.get("carrier", {}).get("title", "АО «СЗППК»")

            route_item = {
                "option_id": f"yandex-{number}-{dep_time.replace(':', '')}",
                "is_direct": True,
                "total_duration_minutes": duration_min,
                "departure_time": dep_time,
                "arrival_time": arr_time,
                "segments": [
                    {
                        "train_number": f"{number} {title}".strip(),
                        "train_type": train_type,
                        "station_from_title": from_title,
                        "station_from_code": st_from.get("code", from_code),
                        "station_to_title": to_title,
                        "station_to_code": st_to.get("code", to_code),
                        "departure_time": dep_time,
                        "arrival_time": arr_time,
                        "delay_minutes": 0,
                        "status": "ON_TIME"
                    }
                ],
                "transfer": None
            }
            routes.append(route_item)

        routes.sort(key=lambda r: self._hhmm_to_minutes(r["departure_time"]))
        return routes

    @staticmethod
    def _extract_hhmm(val: str) -> str:
        if not val:
            return "00:00"
        if "T" in val:
            val = val.split("T")[1]
        parts = val.split(":")
        if len(parts) >= 2:
            return f"{parts[0][-2:]}:{parts[1][:2]}"
        return val

    @staticmethod
    def _hhmm_to_minutes(hhmm: str) -> int:
        try:
            h, m = map(int, hhmm.split(":"))
            return h * 60 + m
        except Exception:
            return 0

    @classmethod
    def _diff_minutes(cls, dep: str, arr: str) -> int:
        d = cls._hhmm_to_minutes(dep)
        a = cls._hhmm_to_minutes(arr)
        if a >= d:
            return a - d
        return (a + 24 * 60) - d

yandex_client = YandexSchedulesClient()
