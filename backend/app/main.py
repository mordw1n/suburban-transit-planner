import sys
import json
import logging
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.redis_client import init_redis_pool, close_redis_pool
from app.api.v1.stations import router as stations_router
from app.api.v1.routes import router as routes_router
from app.api.v1.delays import router as delays_router

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "caller": f"{record.module}:{record.lineno}",
            "msg": record.getMessage()
        }
        return json.dumps(log_obj, ensure_ascii=False)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger("transit.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting transit service...")
    for attempt in range(5):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database schema synchronized successfully.")
            break
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt+1}/5 failed: {e}. Retrying in 2s...")
            await asyncio.sleep(2)
    await init_redis_pool()
    yield
    logger.info("Stopping transit service...")
    await close_redis_pool()
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stations_router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_router, prefix=settings.API_V1_PREFIX)
app.include_router(delays_router, prefix=settings.API_V1_PREFIX)

@app.get("/healthz")
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "database": "connected",
        "redis": "connected",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_url": "/healthz"
    }
