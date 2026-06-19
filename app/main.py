import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.agent.news_agent import get_agent
from app.scheduler import start_scheduler, stop_scheduler
from app.utils.logger import setup_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("news_agent_starting",
                port=os.getenv("PORT", "8001"),
                env=os.getenv("APP_ENV", "development"))

    # Validate critical env vars before starting
    missing = []
    for key in ["OPENAI_API_KEY", "NEWS_API_KEY"]:
        if not os.getenv(key):
            missing.append(key)
    if missing:
        logger.error("missing_env_vars", missing=missing,
                     hint="Set these in Railway → Variables tab")
        raise RuntimeError(f"Missing required env vars: {missing}")

    get_agent()           # warm up agent singleton
    start_scheduler()     # start 7AM daily digest
    yield
    stop_scheduler()
    await get_agent().close()
    logger.info("news_agent_shutdown")


app = FastAPI(
    title="News Summarizer AI Agent",
    description="Daily AI news digest — LangGraph + NewsAPI + GPT-4o-mini",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "News Summarizer AI Agent is running 📰",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
