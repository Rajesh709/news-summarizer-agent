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
    logger.info("news_agent_starting")
    get_agent()                  # warm up the agent singleton
    start_scheduler()            # start daily email scheduler
    yield
    stop_scheduler()
    await get_agent().close()
    logger.info("news_agent_shutdown")


app = FastAPI(
    title="News Summarizer AI Agent",
    description="Natural language news + daily email digest powered by LangGraph + NewsAPI + GPT-4o-mini",
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
        "scheduler": "Daily digest active — 7:00 AM IST",
    }
