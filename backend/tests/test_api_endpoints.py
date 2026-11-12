import pytest
from httpx import AsyncClient

class TestApiEndpoints:
    """Интеграционные тесты REST API эндпоинтов Suburban Transit Planner."""

    @pytest.mark.asyncio
    async def test_get_stations_list(self, async_client: AsyncClient):
        """Проверка эндпоинта /api/v1/stations: возвращает список станций."""
        response = await async_client.get("/api/v1/stations")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 8

        # Проверка обязательных полей станции
        station = data[0]
        assert "id" in station
        assert "code_yandex" in station
        assert "title" in station
        assert "direction" in station
        assert "is_junction" in station

    @pytest.mark.asyncio
    async def test_get_stations_filter_by_direction(self, async_client: AsyncClient):
        """Фильтрация станций по направлению."""
        response = await async_client.get("/api/v1/stations?direction=Финляндское")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        for st in data:
            assert st["direction"] == "Финляндское"

    @pytest.mark.asyncio
    async def test_search_routes_valid_stations(self, async_client: AsyncClient):
        """Поиск маршрутов между Финляндским вокзалом и Зеленогорском."""
        response = await async_client.get("/api/v1/routes/search?from_code=s9602497&to_code=s9602725&date=2026-11-26")
        assert response.status_code == 200
        data = response.json()

        assert data["from_station"]["title"] == "Финляндский вокзал"
        assert data["to_station"]["title"] == "Зеленогорск"
        assert data["search_date"] == "2026-11-26"
        assert "system_status" in data
        assert data["routes_count"] > 0
        assert len(data["routes"]) == data["routes_count"]

    @pytest.mark.asyncio
    async def test_search_routes_legacy_code_support(self, async_client: AsyncClient):
        """Поиск маршрута по устаревшим кодам станций (обратная совместимость)."""
        response = await async_client.get("/api/v1/routes/search?from_code=s9600370&to_code=s9600372")
        assert response.status_code == 200
        data = response.json()
        assert data["from_station"]["title"] == "Финляндский вокзал"
        assert data["routes_count"] > 0

    @pytest.mark.asyncio
    async def test_search_routes_invalid_station_404(self, async_client: AsyncClient):
        """Несуществующий код станции возвращает 404 Not Found."""
        response = await async_client.get("/api/v1/routes/search?from_code=non_existing_st&to_code=s9602725")
        assert response.status_code == 404
        assert "Станция не найдена" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_search_routes_missing_required_params_422(self, async_client: AsyncClient):
        """Отсутствие обязательного параметра from_code или to_code возвращает 422."""
        response = await async_client.get("/api/v1/routes/search?from_code=s9602497")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_delays_live_feed(self, async_client: AsyncClient):
        """Проверка эндпоинта /api/v1/delays/live: возвращает оперативную телеметрию опозданий."""
        response = await async_client.get("/api/v1/delays/live")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            item = data[0]
            assert "train_number" in item
            assert "station_title" in item
            assert "delay_minutes" in item
            assert "status" in item

    @pytest.mark.asyncio
    async def test_health_check_endpoint(self, async_client: AsyncClient):
        """Проверка эндпоинта /api/v1/health: возвращает статус подсистем."""
        response = await async_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["UP", "healthy"]
        assert "version" in data
        assert "database" in data
        assert "redis" in data
