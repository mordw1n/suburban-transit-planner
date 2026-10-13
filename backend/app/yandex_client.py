import logging
import httpx
from typing import Dict, Any, Optional
from app.config import settings
from app.circuit_breaker import yandex_breaker

logger = logging.getLogger("transit.yandex_client")

class YandexSchedulesClient:
    def __init__(self):
        self.api_key = settings.YANDEX_API_KEY
        self.base_url = settings.YANDEX_API_BASE_URL

    async def get_search_schedule(self, from_code: str, to_code: str, date_str: str) -> Optional[Dict[str, Any]]:
        if not yandex_breaker.can_execute():
            logger.warning("Circuit Breaker is OPEN. Skipping external API call.")
            return None

        if not self.api_key:
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
                    return response.json()
                elif response.status_code in [429, 500, 502, 503]:
                    logger.error(f"External API returned {response.status_code}")
                    yandex_breaker.record_failure()
                else:
                    logger.warning(f"Unexpected response status: {response.status_code}")
        except Exception as e:
            logger.error(f"Network error communicating with Yandex API: {e}")
            yandex_breaker.record_failure()

        return None

yandex_client = YandexSchedulesClient()
