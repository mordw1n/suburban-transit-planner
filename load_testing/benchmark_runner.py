import asyncio
import time
import json
import statistics
import sys
from pathlib import Path

# Добавляем backend в sys.path для прямого ASGI тестирования
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import httpx
from app.main import app
from app.circuit_breaker import yandex_breaker, CircuitState

SAMPLE_ROUTES = [
    ("s9602497", "s9602725"),  # Финляндский -> Зеленогорск
    ("s9602497", "s9603175"),  # Финляндский -> Выборг
    ("s9602497", "s9603876"),  # Финляндский -> Девяткино
    ("s9603876", "s9603177"),  # Девяткино -> Приозерск
    ("s9602498", "s9602758"),  # Балтийский -> Гатчина
]

async def run_single_request(client: httpx.AsyncClient, from_code: str, to_code: str):
    t0 = time.perf_counter()
    url = f"/api/v1/routes/search?from_code={from_code}&to_code={to_code}&date=2026-11-26"
    resp = await client.get(url)
    dt = (time.perf_counter() - t0) * 1000.0  # ms
    return resp.status_code, dt, resp.json() if resp.status_code == 200 else None

async def benchmark_concurrency(total_requests: int = 100, concurrency: int = 20):
    print(f"\n=======================================================")
    print(f"Запуск стресс-тестирования: {total_requests} запросов при concurrency={concurrency}")
    print(f"=======================================================")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://benchmark") as client:
        # Прогрев (warmup)
        for f, t in SAMPLE_ROUTES:
            await run_single_request(client, f, t)

        sem = asyncio.Semaphore(concurrency)
        latencies = []
        statuses = []

        async def worker(idx: int):
            f, t = SAMPLE_ROUTES[idx % len(SAMPLE_ROUTES)]
            async with sem:
                status, dt, data = await run_single_request(client, f, t)
                latencies.append(dt)
                statuses.append(status)

        start_time = time.perf_counter()
        tasks = [asyncio.create_task(worker(i)) for i in range(total_requests)]
        await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start_time

    success_count = sum(1 for s in statuses if s == 200)
    rps = total_requests / total_time
    latencies.sort()

    p50 = statistics.median(latencies)
    p90 = latencies[int(len(latencies) * 0.90)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    avg_lat = statistics.mean(latencies)

    results = {
        "total_requests": total_requests,
        "concurrency": concurrency,
        "success_rate_percent": (success_count / total_requests) * 100.0,
        "total_duration_sec": round(total_time, 3),
        "throughput_rps": round(rps, 1),
        "latency_ms": {
            "avg": round(avg_lat, 2),
            "min": round(min(latencies), 2),
            "max": round(max(latencies), 2),
            "p50": round(p50, 2),
            "p90": round(p90, 2),
            "p95": round(p95, 2),
            "p99": round(p99, 2),
        }
    }

    print(f"Выполнено запросов:   {total_requests} (Успешно: {success_count}/{total_requests})")
    print(f"Общее время теста:   {total_time:.3f} сек")
    print(f"Пропускная способность: {rps:.1f} RPS")
    print(f"Задержка (Latency):")
    print(f"  Средняя: {avg_lat:.2f} ms")
    print(f"  Min:     {min(latencies):.2f} ms")
    print(f"  Max:     {max(latencies):.2f} ms")
    print(f"  p50:     {p50:.2f} ms")
    print(f"  p90:     {p90:.2f} ms")
    print(f"  p95:     {p95:.2f} ms")
    print(f"  p99:     {p99:.2f} ms")
    print(f"=======================================================\n")

    return results

async def benchmark_resilience_degradation():
    print(f"=======================================================")
    print(f"Тестирование отказоустойчивости при сбое внешнего API")
    print(f"=======================================================")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://benchmark") as client:
        # Симулируем срабатывание Circuit Breaker
        for _ in range(5):
            yandex_breaker.record_failure()

        assert yandex_breaker.is_degraded() is True

        t0 = time.perf_counter()
        resp = await client.get("/api/v1/routes/search?from_code=s9602497&to_code=s9603175&date=2026-11-26")
        dt = (time.perf_counter() - t0) * 1000.0

        data = resp.json()
        print(f"Статус ответа:           HTTP {resp.status_code}")
        print(f"Флаг деградации:         is_degraded={data.get('is_degraded')}")
        print(f"Статус системы:          system_status='{data.get('system_status')}'")
        print(f"Количество маршрутов:    {data.get('routes_count')} (офлайн-граф)")
        print(f"Время ответа в аварии:   {dt:.2f} ms (SLA < 50ms)")
        print(f"=======================================================\n")

        # Сброс
        yandex_breaker.record_success()

async def main():
    res = await benchmark_concurrency(total_requests=100, concurrency=20)
    await benchmark_resilience_degradation()

    out_file = Path(__file__).resolve().parent / "benchmark_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print(f"Результаты бенчмарка сохранены в {out_file}")

if __name__ == "__main__":
    asyncio.run(main())
