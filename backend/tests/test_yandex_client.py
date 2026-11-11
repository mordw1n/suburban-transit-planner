import pytest
import httpx
from unittest.mock import patch, AsyncMock
from app.yandex_client import yandex_client
from app.circuit_breaker import yandex_breaker, CircuitState

class TestYandexClient:
    """Модульные тесты клиента API Яндекс.Расписаний и парсера ответов."""

    @pytest.fixture(autouse=True)
    def ensure_api_key(self):
        """Гарантирует наличие тестового ключа API для сетевых тестов."""
        orig_key = yandex_client.api_key
        yandex_client.api_key = "mock_api_key_for_testing"
        yield
        yandex_client.api_key = orig_key

    @pytest.mark.asyncio
    async def test_get_search_schedule_success(self, sample_yandex_schedule_response):
        """Успешный запрос (200 OK) возвращает JSON и регистрирует успех в Circuit Breaker."""
        mock_response = httpx.Response(
            status_code=200,
            json=sample_yandex_schedule_response,
            request=httpx.Request("GET", "https://api.rasp.yandex.net/v3.0/search/")
        )

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            res = await yandex_client.get_search_schedule("s9602497", "s9602725", "2026-11-26")

            assert res is not None
            assert "segments" in res
            assert len(res["segments"]) == 2
            assert yandex_breaker.state == CircuitState.CLOSED
            assert yandex_breaker.fail_count == 0

    @pytest.mark.asyncio
    async def test_circuit_breaker_open_skips_call(self):
        """Если Circuit Breaker открыт, запрос не отправляется в сеть."""
        yandex_breaker.state = CircuitState.OPEN

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            res = await yandex_client.get_search_schedule("s9602497", "s9602725", "2026-11-26")
            assert res is None
            mock_get.assert_not_called()

    @pytest.mark.asyncio
    async def test_rate_limit_429_records_failure(self):
        """Превышение лимита запросов (429 Too Many Requests) фиксируется как сбой."""
        mock_response = httpx.Response(
            status_code=429,
            text="Quota exceeded",
            request=httpx.Request("GET", "https://api.rasp.yandex.net/v3.0/search/")
        )

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            res = await yandex_client.get_search_schedule("s9602497", "s9602725", "2026-11-26")

            assert res is None
            assert yandex_breaker.fail_count == 1

    @pytest.mark.asyncio
    async def test_server_error_503_records_failure(self):
        """Ошибка внешнего сервера (503 Service Unavailable) фиксируется как сбой."""
        mock_response = httpx.Response(
            status_code=503,
            text="Service Unavailable",
            request=httpx.Request("GET", "https://api.rasp.yandex.net/v3.0/search/")
        )

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            res = await yandex_client.get_search_schedule("s9602497", "s9602725", "2026-11-26")

            assert res is None
            assert yandex_breaker.fail_count == 1

    @pytest.mark.asyncio
    async def test_network_timeout_records_failure(self):
        """Таймаут сетевого соединения фиксируется как сбой."""
        with patch("httpx.AsyncClient.get", side_effect=httpx.TimeoutException("Read timeout")):
            res = await yandex_client.get_search_schedule("s9602497", "s9602725", "2026-11-26")

            assert res is None
            assert yandex_breaker.fail_count == 1

    @pytest.mark.asyncio
    async def test_missing_api_key_returns_none_safely(self):
        """При отсутствии API ключа метод возвращает None без попытки сетевого вызова."""
        yandex_client.api_key = ""
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            res = await yandex_client.get_search_schedule("s9602497", "s9602725", "2026-11-26")
            assert res is None
            mock_get.assert_not_called()

    def test_parse_yandex_response_express_and_standard(self, sample_yandex_schedule_response):
        """
        Проверка преобразования сырого ответа API Яндекс.Расписаний в унифицированный список RouteOption.
        Экспрессы распознаются как 'Ласточка (Экспресс)', стандартные поезда - 'Стандартная электричка'.
        """
        routes = yandex_client.parse_yandex_response(
            sample_yandex_schedule_response,
            from_code="s9602497",
            to_code="s9602725"
        )

        assert len(routes) == 2

        # Первый поезд - Ласточка (7901)
        r1 = routes[0]
        assert r1["is_direct"] is True
        assert r1["departure_time"] == "07:55"
        assert r1["arrival_time"] == "08:24"
        assert r1["total_duration_minutes"] == 29
        seg1 = r1["segments"][0]
        assert "7901" in seg1["train_number"]
        assert seg1["train_type"] == "Ласточка (Экспресс)"
        assert seg1["station_from_title"] == "Санкт-Петербург (Финляндский вокзал)"
        assert seg1["station_to_title"] == "Зеленогорск"

        # Второй поезд - Стандарт (6115)
        r2 = routes[1]
        assert r2["departure_time"] == "08:15"
        assert r2["arrival_time"] == "09:12"
        assert r2["total_duration_minutes"] == 57
        seg2 = r2["segments"][0]
        assert "6115" in seg2["train_number"]
        assert seg2["train_type"] == "Стандартная электричка"

    def test_parse_yandex_time_helpers(self):
        """Тестирование вспомогательных методов извлечения и парсинга времени."""
        assert yandex_client._extract_hhmm("07:55:00") == "07:55"
        assert yandex_client._extract_hhmm("2026-11-26T07:55:00+03:00") == "07:55"
        assert yandex_client._extract_hhmm("") == "00:00"

        assert yandex_client._hhmm_to_minutes("07:55") == 475
        assert yandex_client._hhmm_to_minutes("00:00") == 0

        assert yandex_client._diff_minutes("07:55", "08:24") == 29
        assert yandex_client._diff_minutes("23:45", "00:15") == 30  # переход через полночь
