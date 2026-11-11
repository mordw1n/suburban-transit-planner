import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.circuit_breaker import yandex_breaker, CircuitState

@pytest.fixture(autouse=True)
def reset_circuit_breaker():
    """Сбрасывает состояние Circuit Breaker перед каждым тестом."""
    yandex_breaker.state = CircuitState.CLOSED
    yandex_breaker.fail_count = 0
    yield
    yandex_breaker.state = CircuitState.CLOSED
    yandex_breaker.fail_count = 0

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Асинхронный HTTP-клиент для тестирования FastAPI эндпоинтов."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

@pytest.fixture
def sample_yandex_schedule_response():
    """Тестовый ответ от API Яндекс.Расписаний."""
    return {
        "search": {
            "from": {"code": "s9602497", "title": "Финляндский вокзал"},
            "to": {"code": "s9602725", "title": "Зеленогорск"},
            "date": "2026-11-26"
        },
        "segments": [
            {
                "thread": {
                    "number": "7901",
                    "title": "Санкт-Петербург — Выборг",
                    "short_title": "СПб — Выборг",
                    "express_type": "express",
                    "transport_type": "suburban",
                    "carrier": {"code": 106, "title": "АО «СЗППК»"}
                },
                "from": {"code": "s9602497", "title": "Санкт-Петербург (Финляндский вокзал)"},
                "to": {"code": "s9602725", "title": "Зеленогорск"},
                "departure": "07:55:00",
                "arrival": "08:24:00",
                "duration": 1740.0,
                "start_date": "2026-11-26"
            },
            {
                "thread": {
                    "number": "6115",
                    "title": "Санкт-Петербург — Зеленогорск",
                    "short_title": "СПб — Зеленогорск",
                    "express_type": None,
                    "transport_type": "suburban",
                    "carrier": {"code": 106, "title": "АО «СЗППК»"}
                },
                "from": {"code": "s9602497", "title": "Санкт-Петербург (Финляндский вокзал)"},
                "to": {"code": "s9602725", "title": "Зеленогорск"},
                "departure": "08:15:00",
                "arrival": "09:12:00",
                "duration": 3420.0,
                "start_date": "2026-11-26"
            }
        ]
    }
