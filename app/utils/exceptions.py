from typing import Optional


class NewsAgentError(Exception):
    """Base exception for the News Summarizer Agent."""


class NewsAPIError(NewsAgentError):
    """Raised when NewsAPI returns an error."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class NoNewsFoundError(NewsAgentError):
    """Raised when no articles are found for the query."""


class RedisConnectionError(NewsAgentError):
    """Raised when Redis is unavailable."""


class AgentError(NewsAgentError):
    """Raised when the LangGraph agent fails."""
