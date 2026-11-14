import random
from locust import HttpUser, task, between

POPULAR_ROUTES = [
    ("s9602497", "s9602725"),  # Финляндский -> Зеленогорск
    ("s9602497", "s9603175"),  # Финляндский -> Выборг
    ("s9602725", "s9603175"),  # Зеленогорск -> Выборг
    ("s9602497", "s9603876"),  # Финляндский -> Девяткино
    ("s9603876", "s9603177"),  # Девяткино -> Приозерск
    ("s9602498", "s9602758"),  # Балтийский -> Гатчина
]

class TransitPlannerUser(HttpUser):
    """
    Модель пользователя пригородной навигационной системы Suburban Transit Planner.
    Имитирует типовое поведение пассажира:
    - 60% поисков маршрутов (проверка расписания электричек)
    - 25% запросов справочника станций и автодополнения
    - 15% мониторинга оперативных задержек (Live Delays)
    """
    wait_time = between(0.5, 2.0)

    @task(6)
    def search_routes(self):
        """Поиск пригородного маршрута с проверкой SLA по задержке."""
        from_code, to_code = random.choice(POPULAR_ROUTES)
        with self.client.get(
            f"/api/v1/routes/search?from_code={from_code}&to_code={to_code}&date=2026-11-26",
            catch_response=True,
            name="/api/v1/routes/search"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "routes" in data and data["routes_count"] >= 0:
                    response.success()
                else:
                    response.failure("Malformed routes response payload")
            else:
                response.failure(f"HTTP status {response.status_code}")

    @task(3)
    def get_stations(self):
        """Запрос справочника станций для выпадающего списка."""
        with self.client.get("/api/v1/stations", catch_response=True, name="/api/v1/stations") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to fetch stations: {response.status_code}")

    @task(1)
    def get_live_delays(self):
        """Просмотр оперативных опозданий поездов."""
        with self.client.get("/api/v1/delays/live", catch_response=True, name="/api/v1/delays/live") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to fetch live delays: {response.status_code}")
