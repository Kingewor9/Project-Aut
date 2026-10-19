"""
Automata TG — FastAPI application entry point.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.db.indexes import create_indexes
from app.db.mongo import close_client
from app.scheduling.scheduler import start_scheduler, stop_scheduler

# Routers
from app.api import users, channels, subscriptions, config as config_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Automata TG API...")
    await create_indexes()
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()
    await close_client()
    logger.info("Automata TG API shut down.")


app = FastAPI(
    title="Automata TG API",
    description="AI-powered content management platform for Telegram channels.",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
origins = settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(users.router, prefix=API_PREFIX)
app.include_router(channels.router, prefix=API_PREFIX)
app.include_router(subscriptions.router, prefix=API_PREFIX)
app.include_router(config_router.router, prefix=API_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "automata-tg"}
