import json
import pytest
from unittest.mock import AsyncMock, patch
import app.redis_client as rc

class TestRedisCache:
    """Модульные тесты кэш-слоя Redis и паттерна Cache-Aside."""

    @pytest.mark.asyncio
    async def test_get_cached_when_redis_none(self):
        """Если Redis недоступен (None), чтение возвращает None без исключения."""
        with patch.object(rc, "redis_pool", None):
            res = await rc.get_cached("some_key")
            assert res is None

    @pytest.mark.asyncio
    async def test_set_cached_when_redis_none(self):
        """Если Redis недоступен (None), запись безопасно игнорируется."""
        with patch.object(rc, "redis_pool", None):
            # Не должно выбрасывать исключение
            await rc.set_cached("some_key", {"data": 123}, ttl_seconds=60)

    @pytest.mark.asyncio
    async def test_cache_hit_returns_deserialized_json(self):
        """Успешный Cache Hit возвращает распарсенный JSON объект."""
        mock_pool = AsyncMock()
        mock_pool.get.return_value = json.dumps([{"option_id": "route-1", "duration": 45}])

        with patch.object(rc, "redis_pool", mock_pool):
            data = await rc.get_cached("routes:s9602497:s9602725:2026-11-26")
            assert data is not None
            assert len(data) == 1
            assert data[0]["option_id"] == "route-1"
            mock_pool.get.assert_called_once_with("routes:s9602497:s9602725:2026-11-26")

    @pytest.mark.asyncio
    async def test_cache_miss_returns_none(self):
        """Cache Miss (ключ отсутствует в Redis) возвращает None."""
        mock_pool = AsyncMock()
        mock_pool.get.return_value = None

        with patch.object(rc, "redis_pool", mock_pool):
            data = await rc.get_cached("routes:nonexistent")
            assert data is None

    @pytest.mark.asyncio
    async def test_set_cached_serializes_with_ttl(self):
        """Запись в кэш сериализует данные и устанавливает правильный TTL."""
        mock_pool = AsyncMock()

        with patch.object(rc, "redis_pool", mock_pool):
            payload = [{"option_id": "test-route"}]
            await rc.set_cached("routes:test_key", payload, ttl_seconds=300)

            mock_pool.set.assert_called_once()
            call_args = mock_pool.set.call_args
            assert call_args[0][0] == "routes:test_key"
            assert "test-route" in call_args[0][1]
            assert call_args[1]["ex"] == 300

    @pytest.mark.asyncio
    async def test_read_error_handled_gracefully(self):
        """Ошибка сокета при чтении из Redis перехватывается, возвращая None."""
        mock_pool = AsyncMock()
        mock_pool.get.side_effect = Exception("Redis connection reset by peer")

        with patch.object(rc, "redis_pool", mock_pool):
            data = await rc.get_cached("routes:error_key")
            assert data is None

    @pytest.mark.asyncio
    async def test_write_error_handled_gracefully(self):
        """Ошибка при записи в Redis логируется без прерывания запроса пользователя."""
        mock_pool = AsyncMock()
        mock_pool.set.side_effect = Exception("Redis out of memory")

        with patch.object(rc, "redis_pool", mock_pool):
            # Не должно выбрасывать исключение
            await rc.set_cached("routes:error_key", {"data": 1}, ttl_seconds=60)
