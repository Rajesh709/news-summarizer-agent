from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.agent.news_agent import get_agent
from app.utils.logger import setup_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("news_agent_starting")
    get_agent()
    yield
    logger.info("news_agent_shutting_down")
    await get_agent().close()


app = FastAPI(
    title="News Summarizer AI Agent",
    description="Natural language news queries powered by LangGraph + NewsAPI + GPT-4o-mini",
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
    return {"message": "News Summarizer AI Agent is running 📰", "docs": "/docs"}
