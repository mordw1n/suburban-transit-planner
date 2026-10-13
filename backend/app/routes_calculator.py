from typing import List, Dict, Any
from datetime import datetime, timedelta

SEED_STATIONS = [
    {
        "id": "st-finlyandsky",
        "code_yandex": "s9600370",
        "title": "Финляндский вокзал",
        "direction": "Финляндское",
        "latitude": 59.9557,
        "longitude": 30.3562,
        "is_junction": True
    },
    {
        "id": "st-vyborg",
        "code_yandex": "s9600371",
        "title": "Выборг",
        "direction": "Финляндское",
        "latitude": 60.7153,
        "longitude": 28.7516,
        "is_junction": False
    },
    {
        "id": "st-zelenogorsk",
        "code_yandex": "s9600372",
        "title": "Зеленогорск",
        "direction": "Финляндское",
        "latitude": 60.1982,
        "longitude": 29.7028,
        "is_junction": True
    },
    {
        "id": "st-devyatkino",
        "code_yandex": "s9600373",
        "title": "Девяткино",
        "direction": "Приозерское",
        "latitude": 60.0504,
        "longitude": 30.4428,
        "is_junction": True
    },
    {
        "id": "st-udelnaya",
        "code_yandex": "s9600374",
        "title": "Удельная",
        "direction": "Финляндское",
        "latitude": 60.0169,
        "longitude": 30.3155,
        "is_junction": True
    },
    {
        "id": "st-priozersk",
        "code_yandex": "s9600375",
        "title": "Приозерск",
        "direction": "Приозерское",
        "latitude": 61.0378,
        "longitude": 30.1264,
        "is_junction": False
    },
    {
        "id": "st-gatchina",
        "code_yandex": "s9600376",
        "title": "Гатчина-Балтийская",
        "direction": "Балтийское",
        "latitude": 59.5664,
        "longitude": 30.1167,
        "is_junction": False
    },
    {
        "id": "st-baltiysky",
        "code_yandex": "s9600377",
        "title": "Балтийский вокзал",
        "direction": "Балтийское",
        "latitude": 59.9072,
        "longitude": 30.2994,
        "is_junction": True
    }
]

SEED_SCHEDULE = [
    {"train": "6115 Ласточка", "type": "Ласточка", "from": "s9600370", "to": "s9600372", "dep": "08:15", "arr": "08:45", "delay": 0, "status": "ON_TIME"},
    {"train": "6127 Стандарт", "type": "Стандарт", "from": "s9600370", "to": "s9600372", "dep": "09:00", "arr": "09:50", "delay": 5, "status": "DELAYED"},
    {"train": "6139 Ласточка", "type": "Ласточка", "from": "s9600370", "to": "s9600372", "dep": "10:10", "arr": "10:40", "delay": 0, "status": "ON_TIME"},
    {"train": "6115 Ласточка", "type": "Ласточка", "from": "s9600372", "to": "s9600371", "dep": "08:48", "arr": "09:30", "delay": 0, "status": "ON_TIME"},
    {"train": "6141 Экспресс", "type": "Экспресс", "from": "s9600372", "to": "s9600371", "dep": "09:05", "arr": "10:02", "delay": 0, "status": "ON_TIME"},
    {"train": "6155 Стандарт", "type": "Стандарт", "from": "s9600372", "to": "s9600371", "dep": "10:05", "arr": "11:15", "delay": 0, "status": "ON_TIME"},
    {"train": "6521 Стандарт", "type": "Стандарт", "from": "s9600370", "to": "s9600373", "dep": "08:30", "arr": "08:55", "delay": 0, "status": "ON_TIME"},
    {"train": "6533 Стандарт", "type": "Стандарт", "from": "s9600370", "to": "s9600373", "dep": "09:20", "arr": "09:45", "delay": 12, "status": "DELAYED"},
    {"train": "6545 Ласточка", "type": "Ласточка", "from": "s9600370", "to": "s9600373", "dep": "10:00", "arr": "10:20", "delay": 0, "status": "ON_TIME"},
    {"train": "6521 Стандарт", "type": "Стандарт", "from": "s9600373", "to": "s9600375", "dep": "09:08", "arr": "11:10", "delay": 0, "status": "ON_TIME"},
    {"train": "6545 Ласточка", "type": "Ласточка", "from": "s9600373", "to": "s9600375", "dep": "10:32", "arr": "12:15", "delay": 0, "status": "ON_TIME"},
    {"train": "6311 Стандарт", "type": "Стандарт", "from": "s9600377", "to": "s9600376", "dep": "08:40", "arr": "09:40", "delay": 0, "status": "ON_TIME"},
    {"train": "6325 Ласточка", "type": "Ласточка", "from": "s9600377", "to": "s9600376", "dep": "09:30", "arr": "10:05", "delay": 0, "status": "ON_TIME"},
    {"train": "6115 Ласточка", "type": "Ласточка", "from": "s9600370", "to": "s9600371", "dep": "08:15", "arr": "09:30", "delay": 0, "status": "ON_TIME"},
    {"train": "6133 Экспресс", "type": "Экспресс", "from": "s9600370", "to": "s9600371", "dep": "10:15", "arr": "11:25", "delay": 0, "status": "ON_TIME"},
    {"train": "6101 Отмененный", "type": "Стандарт", "from": "s9600370", "to": "s9600371", "dep": "11:00", "arr": "12:45", "delay": 0, "status": "CANCELLED"},
]

def parse_time_minutes(t_str: str) -> int:
    h, m = map(int, t_str.split(":"))
    return h * 60 + m

def format_time_minutes(total_m: int) -> str:
    h = (total_m // 60) % 24
    m = total_m % 60
    return f"{h:02d}:{m:02d}"

def calculate_routes(from_code: str, to_code: str) -> List[Dict[str, Any]]:
    results = []

    for item in SEED_SCHEDULE:
        if item["from"] == from_code and item["to"] == to_code:
            dep_m = parse_time_minutes(item["dep"])
            arr_m = parse_time_minutes(item["arr"])
            duration = arr_m - dep_m

            st_from = next((s["title"] for s in SEED_STATIONS if s["code_yandex"] == item["from"]), item["from"])
            st_to = next((s["title"] for s in SEED_STATIONS if s["code_yandex"] == item["to"]), item["to"])

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

    junctions = [s for s in SEED_STATIONS if s["is_junction"] and s["code_yandex"] not in [from_code, to_code]]

    for junction in junctions:
        j_code = junction["code_yandex"]
        first_legs = [item for item in SEED_SCHEDULE if item["from"] == from_code and item["to"] == j_code]
        second_legs = [item for item in SEED_SCHEDULE if item["from"] == j_code and item["to"] == to_code]

        for leg1 in first_legs:
            if leg1.get("status") == "CANCELLED":
                continue
            arr1_m = parse_time_minutes(leg1["arr"]) + leg1.get("delay", 0)

            for leg2 in second_legs:
                if leg2.get("status") == "CANCELLED":
                    continue
                dep2_m = parse_time_minutes(leg2["dep"])
                wait_time = dep2_m - arr1_m

                if 5 <= wait_time <= 45:
                    dep1_m = parse_time_minutes(leg1["dep"])
                    arr2_m = parse_time_minutes(leg2["arr"])
                    total_dur = arr2_m - dep1_m

                    st_from = next((s["title"] for s in SEED_STATIONS if s["code_yandex"] == leg1["from"]), leg1["from"])
                    st_to = next((s["title"] for s in SEED_STATIONS if s["code_yandex"] == leg2["to"]), leg2["to"])
                    is_tight = wait_time < 7

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

    results.sort(key=lambda r: (not r["is_direct"], parse_time_minutes(r["departure_time"])))
    return results
