# Сервис мультимодального планирования пригородных поездок (электрички + пересадки) с учетом задержек и отмен

Учебный курсовой проект по дисциплине **«Конструирование программного обеспечения» (КПО)**  
Санкт-Петербургский политехнический университет Петра Великого (СПбПУ)  
Институт компьютерных наук и кибербезопасности (ИКНК), Высшая школа программной инженерии  

---

## Команда проекта (Группа 5130904/40108)

* **Спиридонов Михаил Павлович** ([@mordw1n](https://github.com/mordw1n)) — *Backend, Data & Fault Tolerance Lead*
* **Абу Блал Абдал Рахман** ([@Xkoex](https://github.com/Xkoex)) — *Frontend, UI/UX & Client Integration Lead*

---

## Технологический стек

* **Backend**: Python 3.12 (FastAPI, асинхронный REST API, Pydantic)
* **База данных**: PostgreSQL 16 (SQLAlchemy asyncpg, реляционная модель, индексы B-Tree)
* **Кэширование и отказоустойчивость**: Redis 7, паттерн **Circuit Breaker** (aiobreaker)
* **Frontend**: Web SPA (React 18, TypeScript, Vite, Tailwind CSS)
* **Внешняя зависимость**: API Яндекс Расписания (нормативные и оперативные графики)
* **Статический анализ безопасности**: Semgrep SAST (CWE-89, CWE-798, CWE-400)
* **Контейнеризация и оркестрация**: Docker Compose

---

## Этапы разработки и документация проекта

1. **Этап 1. Определение проблемы и формулировка темы** — [docs/01-requirements.md#1-определение-проблемы-и-цель-проекта](docs/01-requirements.md)
2. **Этап 2. Выработка требований (User Stories, Масштаб, Fault Tolerance)** — [docs/01-requirements.md](docs/01-requirements.md)
3. **Этап 3. Архитектура и детальное проектирование (C4 Model, API, ER, x10 Scaling)** — [docs/02-architecture.md](docs/02-architecture.md)
4. **Этап 4. Релиз v1.0.0 (FastAPI core, Web SPA, Circuit Breaker, Yandex API)** — [docs/03-release-v1.0.md](docs/03-release-v1.0.md)
5. **Этап 5. Нагрузочное и интеграционное тестирование (E2E, Locust, k6, SLA)** — [docs/04-load-and-integration-testing-report.md](docs/04-load-and-integration-testing-report.md)
6. **Этап 6. Руководство по развертыванию и эксплуатации (Production Runbook)** — [docs/05-assembly-and-deployment-guide.md](docs/05-assembly-and-deployment-guide.md)
7. **Этап 7. Материалы и структура доклада к защите** — [docs/06-project-defense-presentation.md](docs/06-project-defense-presentation.md)

---

## Запуск проекта (Docker Compose)

Запуск всей инфраструктуры (БД, кэш, бэкенд, фронтенд) выполняется одной командой:

```bash
docker compose up --build -d
```

* **Frontend SPA**: `http://localhost:5173`
* **Backend API & Swagger Docs**: `http://localhost:8000/docs`
* **Healthcheck**: `http://localhost:8000/healthz`
