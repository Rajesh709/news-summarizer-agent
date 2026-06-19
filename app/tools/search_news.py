from datetime import datetime, timedelta
from langchain.tools import tool
from app.tools.news_client import NewsClient
from app.tools.top_headlines import _format_articles
from app.utils.exceptions import NewsAPIError, NoNewsFoundError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SearchNewsTool:
    def __init__(self, client: NewsClient) -> None:
        self._client = client

    def as_tool(self):
        client = self._client

        @tool
        async def search_news(query: str, days: int = 1) -> str:
            """Search for news articles about a specific topic, keyword, person,
            company, or event. Use for specific queries like 'news about Tesla',
            'latest AI news', 'Bitcoin today', 'India election news'.
            The 'days' parameter controls how far back to search (1-7 days)."""
            days = max(1, min(days, 7))
            from_date = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

            try:
                data = await client.get("/everything", {
                    "q": query,
                    "from": from_date,
                    "sortBy": "publishedAt",
                    "language": "en",
                    "pageSize": 5,
                })
                articles = data.get("articles", [])
                if not articles:
                    raise NoNewsFoundError(f"No articles found for '{query}'.")

                total = data.get("totalResults", 0)
                header = f"🔍 News Search: **\"{query}\"** (last {days} day{'s' if days > 1 else ''})\n📊 {total} articles found\n\n"
                return header + _format_articles(articles, 5)
            except NoNewsFoundError as exc:
                return f"No news found: {exc}"
            except NewsAPIError as exc:
                logger.error("search_news_error", query=query, error=str(exc))
                return f"Error searching news for '{query}': {exc}"

        return search_news
