import pytest
import time
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from app.circuit_breaker import yandex_breaker, CircuitState

class TestE2ERouteSearchIntegration:
    """
    Сквозные интеграционные тесты жизненного цикла планирования маршрутов.
    Проверяет взаимодействие: HTTP API <-> Поисковый движок <-> Кэш Redis <-> Внешний API <-> Circuit Breaker.
    """

    @pytest.mark.asyncio
    async def test_full_search_flow_with_cache_and_provider_failure(self, async_client: AsyncClient):
        """
        Полный сценарий:
        1. Получение станций из справочника.
        2. Поиск маршрута Финляндский -> Зеленогорск при нормальной работе.
        3. Проверка структуры ответа и наличия прямых поездов.
        4. Эмуляция 5 подряд сбоев внешнего API (429 Rate Limit).
        5. Проверка срабатывания Circuit Breaker и перехода системы в DEGRADED_OFFLINE.
        6. Проверка, что пользователь продолжает получать офлайн-маршруты без падения сервиса.
        """
        # Шаг 1: Запрос списка станций
        stations_resp = await async_client.get("/api/v1/stations")
        assert stations_resp.status_code == 200
        stations = stations_resp.json()
        assert len(stations) >= 6

        fin_station = next(s for s in stations if "Финляндский" in s["title"])
        zel_station = next(s for s in stations if "Зеленогорск" in s["title"])

        # Шаг 2: Поиск маршрута в штатном режиме
        search_resp1 = await async_client.get(
            f"/api/v1/routes/search?from_code={fin_station['code_yandex']}&to_code={zel_station['code_yandex']}&date=2026-11-26"
        )
        assert search_resp1.status_code == 200
        data1 = search_resp1.json()
        assert data1["system_status"] in ["OPERATIONAL", "DEGRADED_OFFLINE"]
        assert data1["routes_count"] > 0
        assert data1["from_station"]["id"] == fin_station["id"]
        assert data1["to_station"]["id"] == zel_station["id"]

        # Шаг 3: Проверка повторного запроса (проверка согласованности кэшированного ответа)
        search_resp2 = await async_client.get(
            f"/api/v1/routes/search?from_code={fin_station['code_yandex']}&to_code={zel_station['code_yandex']}&date=2026-11-26"
        )
        assert search_resp2.status_code == 200
        data2 = search_resp2.json()
        assert data2["routes_count"] == data1["routes_count"]

        # Шаг 4: Эмуляция сбоя внешнего провайдера (исчерпание суточного лимита 500 запросов -> HTTP 429)
        for _ in range(5):
            yandex_breaker.record_failure()

        assert yandex_breaker.state == CircuitState.OPEN
        assert yandex_breaker.is_degraded() is True

        # Шаг 5: Запрос нового направления при открытом Circuit Breaker (например, Финляндский -> Выборг)
        vyb_station = next(s for s in stations if "Выборг" in s["title"])
        search_resp_degraded = await async_client.get(
            f"/api/v1/routes/search?from_code={fin_station['code_yandex']}&to_code={vyb_station['code_yandex']}&date=2026-11-26"
        )

        assert search_resp_degraded.status_code == 200
        data_deg = search_resp_degraded.json()
        # Сервис не упал, а корректно отдал ответ с флагом деградации и локальными маршрутами
        assert data_deg["is_degraded"] is True
        assert data_deg["system_status"] == "DEGRADED_OFFLINE"
        assert data_deg["routes_count"] > 0
        assert any(r["is_direct"] for r in data_deg["routes"])

    @pytest.mark.asyncio
    async def test_transfer_route_e2e_data_integrity(self, async_client: AsyncClient):
        """Интеграционная проверка корректности данных пересадочных сегментов."""
        # s9602497 (Финляндский) -> s9603175 (Выборг)
        resp = await async_client.get("/api/v1/routes/search?from_code=s9602497&to_code=s9603175&date=2026-11-26")
        assert resp.status_code == 200
        data = resp.json()

        transfer_options = [r for r in data["routes"] if not r["is_direct"]]
        assert len(transfer_options) > 0

        first_transfer = transfer_options[0]
        assert len(first_transfer["segments"]) == 2
        seg1 = first_transfer["segments"][0]
        seg2 = first_transfer["segments"][1]

        # Прибытие первого сегмента должно совпадать со станцией пересадки
        assert seg1["station_to_title"] == first_transfer["transfer"]["junction_station_title"]
        assert seg2["station_from_title"] == first_transfer["transfer"]["junction_station_title"]

        # Время ожидания должно быть положительным
        assert first_transfer["transfer"]["wait_time_minutes"] >= 5
