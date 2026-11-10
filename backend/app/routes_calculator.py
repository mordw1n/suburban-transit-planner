import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("transit.routes_calculator")

# Словарь синонимов и кодов станций (поддержка реальных кодов Яндекс.Расписаний и тестовых алиасов)
STATION_ALIASES: Dict[str, str] = {
    # Тестовые коды -> Реальные коды Яндекс.Расписаний
    "s9600370": "s9602497",  # Финляндский вокзал
    "s9600371": "s9603175",  # Выборг
    "s9600372": "s9602725",  # Зеленогорск
    "s9600373": "s9603876",  # Девяткино
    "s9600374": "s9603463",  # Удельная
    "s9600375": "s9603177",  # Приозерск
    "s9600376": "s9602758",  # Гатчина-Балтийская
    "s9600377": "s9602498",  # Балтийский вокзал
}

def normalize_station_code(code: str) -> str:
    """Приводит код станции к единому каноническому виду (поддерживает алиасы)."""
    return STATION_ALIASES.get(code, code)

SEED_STATIONS = [
    {
        "id": "st-finlyandsky",
        "code_yandex": "s9602497",
        "legacy_code": "s9600370",
        "title": "Финляндский вокзал",
        "direction": "Финляндское",
        "latitude": 59.9557,
        "longitude": 30.3562,
        "is_junction": True
    },
    {
        "id": "st-udelnaya",
        "code_yandex": "s9603463",
        "legacy_code": "s9600374",
        "title": "Удельная",
        "direction": "Финляндское",
        "latitude": 60.0169,
        "longitude": 30.3155,
        "is_junction": True
    },
    {
        "id": "st-zelenogorsk",
        "code_yandex": "s9602725",
        "legacy_code": "s9600372",
        "title": "Зеленогорск",
        "direction": "Финляндское",
        "latitude": 60.1982,
        "longitude": 29.7028,
        "is_junction": True
    },
    {
        "id": "st-vyborg",
        "code_yandex": "s9603175",
        "legacy_code": "s9600371",
        "title": "Выборг",
        "direction": "Финляндское",
        "latitude": 60.7153,
        "longitude": 28.7516,
        "is_junction": False
    },
    {
        "id": "st-devyatkino",
        "code_yandex": "s9603876",
        "legacy_code": "s9600373",
        "title": "Девяткино",
        "direction": "Приозерское",
        "latitude": 60.0504,
        "longitude": 30.4428,
        "is_junction": True
    },
    {
        "id": "st-priozersk",
        "code_yandex": "s9603177",
        "legacy_code": "s9600375",
        "title": "Приозерск",
        "direction": "Приозерское",
        "latitude": 61.0378,
        "longitude": 30.1264,
        "is_junction": False
    },
    {
        "id": "st-baltiysky",
        "code_yandex": "s9602498",
        "legacy_code": "s9600377",
        "title": "Балтийский вокзал",
        "direction": "Балтийское",
        "latitude": 59.9072,
        "longitude": 30.2994,
        "is_junction": True
    },
    {
        "id": "st-gatchina",
        "code_yandex": "s9602758",
        "legacy_code": "s9600376",
        "title": "Гатчина-Балтийская",
        "direction": "Балтийское",
        "latitude": 59.5664,
        "longitude": 30.1167,
        "is_junction": False
    }
]

# Офлайн-расписание для автономной работы и Graceful Degradation
SEED_SCHEDULE = [
    # Финляндский -> Зеленогорск
    {"train": "6115 Ласточка", "type": "Ласточка", "from": "s9602497", "to": "s9602725", "dep": "08:15", "arr": "08:45", "delay": 0, "status": "ON_TIME"},
    {"train": "6127 Стандарт", "type": "Стандарт", "from": "s9602497", "to": "s9602725", "dep": "09:00", "arr": "09:50", "delay": 5, "status": "DELAYED"},
    {"train": "6139 Ласточка", "type": "Ласточка", "from": "s9602497", "to": "s9602725", "dep": "10:10", "arr": "10:40", "delay": 0, "status": "ON_TIME"},
    
    # Зеленогорск -> Выборг
    {"train": "6115 Ласточка", "type": "Ласточка", "from": "s9602725", "to": "s9603175", "dep": "08:48", "arr": "09:30", "delay": 0, "status": "ON_TIME"},
    {"train": "6141 Экспресс", "type": "Экспресс", "from": "s9602725", "to": "s9603175", "dep": "09:05", "arr": "10:02", "delay": 0, "status": "ON_TIME"},
    {"train": "6155 Стандарт", "type": "Стандарт", "from": "s9602725", "to": "s9603175", "dep": "10:05", "arr": "11:15", "delay": 0, "status": "ON_TIME"},
    
    # Прямые Финляндский -> Выборг
    {"train": "7901 Ласточка", "type": "Ласточка", "from": "s9602497", "to": "s9603175", "dep": "07:55", "arr": "09:07", "delay": 0, "status": "ON_TIME"},
    {"train": "6121 Стандарт", "type": "Стандарт", "from": "s9602497", "to": "s9603175", "dep": "08:15", "arr": "09:30", "delay": 0, "status": "ON_TIME"},
    {"train": "6133 Экспресс", "type": "Экспресс", "from": "s9602497", "to": "s9603175", "dep": "10:15", "arr": "11:25", "delay": 0, "status": "ON_TIME"},
    {"train": "6101 Отмененный", "type": "Стандарт", "from": "s9602497", "to": "s9603175", "dep": "11:00", "arr": "12:45", "delay": 0, "status": "CANCELLED"},

    # Приозерское направление: Финляндский -> Девяткино -> Приозерск
    {"train": "6521 Стандарт", "type": "Стандарт", "from": "s9602497", "to": "s9603876", "dep": "08:30", "arr": "08:55", "delay": 0, "status": "ON_TIME"},
    {"train": "6533 Стандарт", "type": "Стандарт", "from": "s9602497", "to": "s9603876", "dep": "09:20", "arr": "09:45", "delay": 12, "status": "DELAYED"},
    {"train": "6545 Ласточка", "type": "Ласточка", "from": "s9602497", "to": "s9603876", "dep": "10:00", "arr": "10:20", "delay": 0, "status": "ON_TIME"},
    {"train": "6521 Стандарт", "type": "Стандарт", "from": "s9603876", "to": "s9603177", "dep": "09:08", "arr": "11:10", "delay": 0, "status": "ON_TIME"},
    {"train": "6545 Ласточка", "type": "Ласточка", "from": "s9603876", "to": "s9603177", "dep": "10:32", "arr": "12:15", "delay": 0, "status": "ON_TIME"},

    # Балтийское направление
    {"train": "6311 Стандарт", "type": "Стандарт", "from": "s9602498", "to": "s9602758", "dep": "08:40", "arr": "09:40", "delay": 0, "status": "ON_TIME"},
    {"train": "6325 Ласточка", "type": "Ласточка", "from": "s9602498", "to": "s9602758", "dep": "09:30", "arr": "10:05", "delay": 0, "status": "ON_TIME"},
]

def find_station_by_code(code: str) -> Optional[Dict[str, Any]]:
    """Находит станцию по коду (с учетом реального и устаревшего кода)."""
    norm = normalize_station_code(code)
    for s in SEED_STATIONS:
        if s["code_yandex"] == norm or s.get("legacy_code") == code or s["code_yandex"] == code:
            return s
    return None

def parse_time_minutes(t_str: str) -> int:
    h, m = map(int, t_str.split(":"))
    return h * 60 + m

def format_time_minutes(total_m: int) -> str:
    h = (total_m // 60) % 24
    m = total_m % 60
    return f"{h:02d}:{m:02d}"

def calculate_routes(from_code: str, to_code: str) -> List[Dict[str, Any]]:
    """
    Расчет прямых и пересадочных маршрутов по графу пригородного сообщения.
    Учитывает:
    - Фильтрацию отмененных рейсов (CANCELLED)
    - Поиск стыковок через пересадочные узлы (junctions)
    - Минимальный интервал пересадки (5-45 минут)
    - Безопасный буфер пешеходного перехода (7 минут, флаг is_tight_connection)
    - Сортировку: приоритет прямым рейсам, затем по времени отправления
    """
    norm_from = normalize_station_code(from_code)
    norm_to = normalize_station_code(to_code)

    results: List[Dict[str, Any]] = []

    # 1. Поиск прямых маршрутов
    for item in SEED_SCHEDULE:
        if item["from"] == norm_from and item["to"] == norm_to:
            if item.get("status") == "CANCELLED":
                logger.info(f"[EXCLUDE CANCELLED] Skipped direct train {item['train']} due to CANCELLED status")
                continue

            dep_m = parse_time_minutes(item["dep"])
            arr_m = parse_time_minutes(item["arr"])
            duration = arr_m - dep_m

            st_from_obj = find_station_by_code(item["from"])
            st_to_obj = find_station_by_code(item["to"])
            st_from = st_from_obj["title"] if st_from_obj else item["from"]
            st_to = st_to_obj["title"] if st_to_obj else item["to"]

            logger.info(f"[DIRECT MATCH] {item['train']} ({item['type']}): {st_from} -> {st_to}, {item['dep']}-{item['arr']}, status={item.get('status')}")

            results.append({
                "option_id": f"direct-{item['train']}-{item['dep']}",
                "is_direct": True,
                "total_duration_minutes": duration,
                "departure_time": item["dep"],
                "arrival_time": item["arr"],
                "segments": [
                    {
                        "train_number": item["train"],
                        "train_type": item["type"],
                        "station_from_title": st_from,
                        "station_from_code": item["from"],
                        "station_to_title": st_to,
                        "station_to_code": item["to"],
                        "departure_time": item["dep"],
                        "arrival_time": item["arr"],
                        "delay_minutes": item.get("delay", 0),
                        "status": item.get("status", "ON_TIME")
                    }
                ],
                "transfer": None
            })

    # 2. Поиск маршрутов с 1 пересадкой через узловые станции (Junctions)
    junctions = [
        s for s in SEED_STATIONS 
        if s["is_junction"] and s["code_yandex"] not in [norm_from, norm_to]
    ]

    for junction in junctions:
        j_code = junction["code_yandex"]
        first_legs = [item for item in SEED_SCHEDULE if item["from"] == norm_from and item["to"] == j_code]
        second_legs = [item for item in SEED_SCHEDULE if item["from"] == j_code and item["to"] == norm_to]

        for leg1 in first_legs:
            if leg1.get("status") == "CANCELLED":
                continue
            arr1_m = parse_time_minutes(leg1["arr"]) + leg1.get("delay", 0)

            for leg2 in second_legs:
                if leg2.get("status") == "CANCELLED":
                    continue
                dep2_m = parse_time_minutes(leg2["dep"])
                wait_time = dep2_m - arr1_m

                # Допустимое окно стыковки: от 5 до 45 минут
                if 5 <= wait_time <= 45:
                    dep1_m = parse_time_minutes(leg1["dep"])
                    arr2_m = parse_time_minutes(leg2["arr"])
                    total_dur = arr2_m - dep1_m

                    st_from_obj = find_station_by_code(leg1["from"])
                    st_to_obj = find_station_by_code(leg2["to"])
                    st_from = st_from_obj["title"] if st_from_obj else leg1["from"]
                    st_to = st_to_obj["title"] if st_to_obj else leg2["to"]
                    
                    # Буфер перехода: менее 7 минут считается рискованной пересадкой
                    is_tight = wait_time < 7

                    logger.info(
                        f"[TRANSFER MATCH] Hub: {junction['title']}, Leg1: {leg1['train']} (arr {leg1['arr']}), "
                        f"Leg2: {leg2['train']} (dep {leg2['dep']}), Wait: {wait_time}m, Buffer: 7m, Tight: {is_tight}"
                    )

                    results.append({
                        "option_id": f"transfer-{leg1['train']}-{leg2['train']}-{leg1['dep']}",
                        "is_direct": False,
                        "total_duration_minutes": total_dur,
                        "departure_time": leg1["dep"],
                        "arrival_time": leg2["arr"],
                        "segments": [
                            {
                                "train_number": leg1["train"],
                                "train_type": leg1["type"],
                                "station_from_title": st_from,
                                "station_from_code": leg1["from"],
                                "station_to_title": junction["title"],
                                "station_to_code": j_code,
                                "departure_time": leg1["dep"],
                                "arrival_time": leg1["arr"],
                                "delay_minutes": leg1.get("delay", 0),
                                "status": leg1.get("status", "ON_TIME")
                            },
                            {
                                "train_number": leg2["train"],
                                "train_type": leg2["type"],
                                "station_from_title": junction["title"],
                                "station_from_code": j_code,
                                "station_to_title": st_to,
                                "station_to_code": leg2["to"],
                                "departure_time": leg2["dep"],
                                "arrival_time": leg2["arr"],
                                "delay_minutes": leg2.get("delay", 0),
                                "status": leg2.get("status", "ON_TIME")
                            }
                        ],
                        "transfer": {
                            "junction_station_title": junction["title"],
                            "junction_station_code": j_code,
                            "wait_time_minutes": wait_time,
                            "walking_buffer_minutes": 7,
                            "is_tight_connection": is_tight
                        }
                    })

    # Сортировка: сначала прямые рейсы, затем по времени отправления
    results.sort(key=lambda r: (not r["is_direct"], parse_time_minutes(r["departure_time"])))
    return results
