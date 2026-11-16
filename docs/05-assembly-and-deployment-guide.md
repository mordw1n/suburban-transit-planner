# Руководство по сборке, развертыванию и эксплуатации (Runbook)
## Проект: Suburban Transit Planner
**Этап:** Сборка, упаковка и защита (10.12.2026)  
**Авторы:** Спиридонов М. П. (`mordw1n`), Абу Блал А. Р. (`abdal.rahman`)

---

## 1. Системные требования

### Минимальные аппаратные требования:
- **Процессор:** 2 ядра (x86_64 / ARM64)
- **Оперативная память:** 2 ГБ RAM (рекомендуется 4 ГБ)
- **Дисковое пространство:** 5 ГБ свободного места

### Программное окружение:
- **Docker Engine:** версия 24.0+
- **Docker Compose:** версия v2.20+
- **Python:** 3.12 (для локальной разработки вне контейнеров)
- **Node.js:** 20 LTS (для сборки frontend артефактов)

---

## 2. Карта портов и сетевая топология

| Сервис | Внутренний порт | Внешний порт | Назначение |
| :--- | :---: | :---: | :--- |
| **transit-frontend** | `80/tcp` | `80`, `3000` | Nginx Static Reverse Proxy, React SPA интерфейс |
| **transit-backend** | `8000/tcp` | `8000` | FastAPI ASGI REST Gateway, Swagger UI (`/docs`) |
| **transit-postgres** | `5432/tcp` | `5432` | Реляционная СУБД PostgreSQL 16 (справочники, журнал) |
| **transit-redis** | `6379/tcp` | `6379` | In-memory хранилище кэша маршрутов и телеметрии |

---

## 3. Настройка переменных окружения (`.env`)

Создайте файл `.env` в корневой директории проекта:

```bash
# База данных PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=transit_planner
DATABASE_URL=postgresql+asyncpg://postgres:postgres@transit-postgres:5432/transit_planner

# Кэш-сервер Redis
REDIS_URL=redis://transit-redis:6379/0

# Интеграция с API Яндекс.Расписаний
YANDEX_API_KEY=9767995c-25ed-4c04-a367-0a8368dee2e2
YANDEX_API_BASE_URL=https://api.rasp.yandex.net/v3.0

# Параметры отказоустойчивости Circuit Breaker
CIRCUIT_BREAKER_FAIL_MAX=5
CIRCUIT_BREAKER_RESET_TIMEOUT=60
```

---

## 4. Сборка и запуск в Production режиме

### 4.1. Автоматическая сборка и развертывание:
```bash
# 1. Клонирование репозитория
git clone https://github.com/mordw1n/suburban-transit-planner.git
cd suburban-transit-planner

# 2. Сборка всех Docker-образов и запуск контейнеров в фоне
docker compose -f docker-compose.prod.yml up -d --build
```

### 4.2. Контроль статуса контейнеров:
```bash
docker compose -f docker-compose.prod.yml ps
```
Ожидаемый статус всех сервисов — `Up (healthy)`.

---

## 5. Проверка работоспособности (Healthchecks & Telemetry)

1. **Проверка системного статуса бэкенда:**
   ```bash
   curl -s http://localhost:8000/healthz | jq .
   ```
   Ожидаемый ответ:
   ```json
   {
     "status": "healthy",
     "version": "0.1.0-mvp",
     "database": "connected",
     "redis": "connected"
   }
   ```

2. **Проверка сквозного поиска маршрута:**
   ```bash
   curl -s "http://localhost:8000/api/v1/routes/search?from_code=s9602497&to_code=s9602725" | jq .
   ```

3. **Просмотр логов в реальном времени:**
   ```bash
   # Логирование маршрутизатора и кэша
   docker logs -f transit-backend-prod --tail 50
   ```

---

## 6. Процедура аварийного переключения (Disaster Recovery)

В случае исчерпания суточного лимита внешнего API (500 запросов) или сетевого разрыва:
1. Автомат **Circuit Breaker** фиксирует 5 ошибок и изолирует внешний контур.
2. В логах появляется запись: `[ERROR] Circuit Breaker tripped to OPEN, timeout: 60s`.
3. Система автоматически отдает клиентам расписание из локального расчетного графа.
4. В ответе клиенту выставляется флаг `"is_degraded": true`, а в веб-интерфейсе появляется предупреждающий баннер: *«Режим ограниченной функциональности: отображается офлайн-расписание»*.
5. Никаких ручных действий оператора не требуется: сервис восстановится автоматически при возобновлении связи.

---

## 7. Остановка и обновление системы

```bash
# Корректная остановка без потери данных в томах
docker compose -f docker-compose.prod.yml down

# Обновление и перезапуск
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build
```
