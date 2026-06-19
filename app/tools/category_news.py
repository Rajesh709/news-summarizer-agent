from datetime import datetime
from langchain.tools import tool
from app.tools.news_client import NewsClient
from app.tools.top_headlines import _format_articles
from app.utils.exceptions import NewsAPIError, NoNewsFoundError
from app.utils.logger import get_logger

logger = get_logger(__name__)

VALID_CATEGORIES = ["business", "entertainment", "general", "health", "science", "sports", "technology"]

CATEGORY_EMOJIS = {
    "business": "💼",
    "entertainment": "🎬",
    "general": "🌐",
    "health": "🏥",
    "science": "🔬",
    "sports": "⚽",
    "technology": "💻",
}


class CategoryNewsTool:
    def __init__(self, client: NewsClient) -> None:
        self._client = client

    def as_tool(self):
        client = self._client

        @tool
        async def get_category_news(category: str, country: str = "us") -> str:
            """Get top news by category. Available categories:
            business, entertainment, general, health, science, sports, technology.
            Use when user asks for news about a specific topic like
            'sports news', 'tech news today', 'health news', 'business headlines'."""
            category = category.lower().strip()
            if category not in VALID_CATEGORIES:
                return (
                    f"Invalid category '{category}'. "
                    f"Choose from: {', '.join(VALID_CATEGORIES)}"
                )
            emoji = CATEGORY_EMOJIS.get(category, "📰")
            try:
                data = await client.get("/top-headlines", {
                    "category": category,
                    "country": country.lower(),
                    "pageSize": 5,
                })
                articles = data.get("articles", [])
                if not articles:
                    raise NoNewsFoundError(f"No {category} news found.")

                total = data.get("totalResults", 0)
                header = (
                    f"{emoji} **{category.title()} News** ({country.upper()}) "
                    f"— {datetime.utcnow().strftime('%b %d, %Y')}\n"
                    f"📊 {total} articles available\n\n"
                )
                return header + _format_articles(articles, 5)
            except NoNewsFoundError as exc:
                return f"No news found: {exc}"
            except NewsAPIError as exc:
                logger.error("category_news_error", category=category, error=str(exc))
                return f"Error fetching {category} news: {exc}"

        return get_category_news
