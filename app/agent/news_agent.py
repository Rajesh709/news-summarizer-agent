from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from app.config import get_settings
from app.tools.news_client import NewsClient
from app.tools.top_headlines import TopHeadlinesTool
from app.tools.search_news import SearchNewsTool
from app.tools.category_news import CategoryNewsTool
from app.tools.trending_topics import TrendingTopicsTool
from app.tools.country_news import CountryNewsTool
from app.memory.redis_memory import get_redis_url
from app.agent.prompts import SYSTEM_PROMPT
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NewsAgent:
    """LangGraph ReAct agent for news summarization with Redis memory."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = NewsClient()
        self._redis_url = get_redis_url()
        self._redis_ttl = settings.redis_ttl

        self._llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.2,
        )

        # Register all tools
        self._tools = [
            TopHeadlinesTool(self._client).as_tool(),
            SearchNewsTool(self._client).as_tool(),
            CategoryNewsTool(self._client).as_tool(),
            TrendingTopicsTool(self._client).as_tool(),
            CountryNewsTool(self._client).as_tool(),
        ]

        self._checkpointer = MemorySaver()
        self._graph = create_react_agent(
            self._llm,
            tools=self._tools,
            checkpointer=self._checkpointer,
            prompt=SYSTEM_PROMPT,
        )

    def _load_history(self, session_id: str) -> list:
        try:
            history = RedisChatMessageHistory(
                session_id=session_id,
                url=self._redis_url,
                ttl=self._redis_ttl,
                key_prefix="news_agent:chat:",
            )
            return history.messages
        except Exception as exc:
            logger.warning("redis_load_failed", session_id=session_id, error=str(exc))
            return []

    def _save_history(self, session_id: str, human: str, ai: str) -> None:
        try:
            history = RedisChatMessageHistory(
                session_id=session_id,
                url=self._redis_url,
                ttl=self._redis_ttl,
                key_prefix="news_agent:chat:",
            )
            history.add_user_message(human)
            history.add_ai_message(ai)
        except Exception as exc:
            logger.warning("redis_save_failed", session_id=session_id, error=str(exc))

    async def chat(self, session_id: str, user_message: str) -> str:
        logger.info("news_agent_chat", session_id=session_id)
        try:
            prior = self._load_history(session_id)
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + prior + [HumanMessage(content=user_message)]
            config = {"configurable": {"thread_id": session_id}}
            result = await self._graph.ainvoke({"messages": messages}, config=config)
            ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
            response = ai_messages[-1].content if ai_messages else "I could not generate a response."
            self._save_history(session_id, user_message, response)
            logger.info("news_agent_response", session_id=session_id)
            return response
        except Exception as exc:
            logger.error("news_agent_error", session_id=session_id, error=str(exc))
            return f"Error processing your request: {exc}"

    async def close(self) -> None:
        await self._client.close()


_agent_instance: Optional[NewsAgent] = None


def get_agent() -> NewsAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = NewsAgent()
    return _agent_instance
