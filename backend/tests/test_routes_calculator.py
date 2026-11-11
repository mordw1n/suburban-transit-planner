import pytest
from app.routes_calculator import (
    calculate_routes,
    parse_time_minutes,
    format_time_minutes,
    normalize_station_code,
    find_station_by_code,
    SEED_STATIONS
)

class TestRoutesCalculator:
    """Модульные тесты алгоритма расчета маршрутов и пересадочного буфера."""

    def test_direct_routes_found(self):
        """Проверка нахождения прямых рейсов между станциями."""
        # Финляндский вокзал -> Зеленогорск
        routes = calculate_routes("s9602497", "s9602725")
        assert len(routes) >= 3
        direct_routes = [r for r in routes if r["is_direct"]]
        assert len(direct_routes) >= 3

        first = direct_routes[0]
        assert first["is_direct"] is True
        assert first["departure_time"] == "08:15"
        assert first["arrival_time"] == "08:45"
        assert first["total_duration_minutes"] == 30
        assert len(first["segments"]) == 1
        assert first["transfer"] is None

    def test_transfer_routes_via_zelenogorsk(self):
        """Проверка построения пересадочного маршрута через узловую станцию Зеленогорск."""
        # Финляндский -> Выборг
        routes = calculate_routes("s9602497", "s9603175")
        assert len(routes) > 0

        transfer_routes = [r for r in routes if not r["is_direct"]]
        assert len(transfer_routes) >= 1

        transfer = transfer_routes[0]
        assert transfer["is_direct"] is False
        assert len(transfer["segments"]) == 2
        assert transfer["transfer"] is not None
        assert transfer["transfer"]["junction_station_code"] == "s9602725"
        assert transfer["transfer"]["junction_station_title"] == "Зеленогорск"
        assert transfer["transfer"]["walking_buffer_minutes"] == 7

    def test_transfer_walking_buffer_and_tight_connection(self):
        """
        Проверка бизнес-правила безопасности пересадки:
        Если время ожидания < 7 минут, выставляется флаг is_tight_connection = True.
        """
        routes = calculate_routes("s9602497", "s9603175")
        transfer_routes = [r for r in routes if not r["is_direct"]]

        for tr in transfer_routes:
            wait = tr["transfer"]["wait_time_minutes"]
            is_tight = tr["transfer"]["is_tight_connection"]
            if wait < 7:
                assert is_tight is True, f"Ожидание {wait} мин должно быть помечено как tight!"
            else:
                assert is_tight is False, f"Ожидание {wait} мин не должно быть tight!"

    def test_cancelled_trains_filtered_out(self):
        """Отмененные рейсы (status == CANCELLED) должны исключаться из результатов."""
        routes = calculate_routes("s9602497", "s9603175")
        train_names = []
        for r in routes:
            for s in r["segments"]:
                train_names.append(s["train_number"])

        assert not any("Отмененный" in name for name in train_names)
        assert not any("6101" in name for name in train_names)

    def test_sorting_order_direct_first_then_departure_time(self):
        """
        Проверка сортировки: прямые рейсы идут раньше пересадочных,
        внутри каждой группы - по возрастанию времени отправления.
        """
        routes = calculate_routes("s9602497", "s9603175")
        assert len(routes) >= 2

        # Все прямые рейсы должны предшествовать пересадочным
        direct_seen = False
        transfer_seen = False
        for r in routes:
            if r["is_direct"]:
                assert not transfer_seen, "Прямой маршрут найден после пересадочного!"
                direct_seen = True
            else:
                transfer_seen = True

        # Проверка хронологического порядка среди прямых
        directs = [r for r in routes if r["is_direct"]]
        for i in range(len(directs) - 1):
            t1 = parse_time_minutes(directs[i]["departure_time"])
            t2 = parse_time_minutes(directs[i + 1]["departure_time"])
            assert t1 <= t2, "Прямые рейсы должны быть отсортированы по времени отправления!"

    def test_station_aliases_compatibility(self):
        """Проверка обратной совместимости устаревших кодов станций (s9600370 -> s9602497)."""
        routes_new = calculate_routes("s9602497", "s9602725")
        routes_legacy = calculate_routes("s9600370", "s9600372")

        assert len(routes_new) == len(routes_legacy)
        assert routes_new[0]["departure_time"] == routes_legacy[0]["departure_time"]

    def test_unconnected_stations_returns_empty(self):
        """Запрос между изолированными станциями возвращает пустой список."""
        # Приозерск -> Гатчина (нет прямых или 1-пересадочных связей на полигоне)
        routes = calculate_routes("s9603177", "s9602758")
        assert routes == []

    def test_time_parsing_and_formatting(self):
        """Проверка вспомогательных функций работы со временем."""
        assert parse_time_minutes("00:00") == 0
        assert parse_time_minutes("08:15") == 495
        assert parse_time_minutes("23:59") == 1439

        assert format_time_minutes(0) == "00:00"
        assert format_time_minutes(495) == "08:15"
        assert format_time_minutes(1440) == "00:00"

    def test_find_station_by_code(self):
        """Поиск станции по реальному коду, устаревшему коду и обработка неизвестных кодов."""
        st1 = find_station_by_code("s9602497")
        assert st1 is not None
        assert st1["title"] == "Финляндский вокзал"

        st2 = find_station_by_code("s9600370")
        assert st2 is not None
        assert st2["title"] == "Финляндский вокзал"

        st_none = find_station_by_code("unknown_station_code")
        assert st_none is None
