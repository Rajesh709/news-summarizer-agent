from datetime import datetime
from langchain.tools import tool
from app.tools.news_client import NewsClient
from app.utils.exceptions import NewsAPIError, NoNewsFoundError
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _format_articles(articles: list, max_articles: int = 5) -> str:
    lines = []
    for i, article in enumerate(articles[:max_articles], 1):
        title = article.get("title", "No title")
        source = article.get("source", {}).get("name", "Unknown")
        published = article.get("publishedAt", "")
        url = article.get("url", "")
        description = article.get("description") or ""

        if published:
            try:
                dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                published = dt.strftime("%b %d, %Y %I:%M %p UTC")
            except Exception:
                pass

        lines.append(
            f"📰 **{i}. {title}**\n"
            f"   🔖 Source: {source} | 🕐 {published}\n"
            f"   📝 {description[:150]}{'...' if len(description) > 150 else ''}\n"
            f"   🔗 {url}"
        )
    return "\n\n".join(lines)


class TopHeadlinesTool:
    def __init__(self, client: NewsClient) -> None:
        self._client = client

    def as_tool(self):
        client = self._client

        @tool
        async def get_top_headlines(country: str = "us") -> str:
            """Get today's top news headlines. Optionally filter by country code
            (e.g., 'us', 'in', 'gb', 'au'). Returns the top 5 headlines with
            source, time, description and link. Use for general news queries
            like 'What's in the news today?' or 'Show me today's top stories'."""
            try:
                data = await client.get("/top-headlines", {"country": country.lower(), "pageSize": 5})
                articles = data.get("articles", [])
                if not articles:
                    raise NoNewsFoundError(f"No headlines found for country '{country}'.")

                total = data.get("totalResults", 0)
                header = f"🌍 Top Headlines ({country.upper()}) — {datetime.utcnow().strftime('%b %d, %Y')}\n📊 {total} total articles found\n\n"
                return header + _format_articles(articles, 5)
            except NoNewsFoundError as exc:
                return f"No news found: {exc}"
            except NewsAPIError as exc:
                logger.error("top_headlines_error", error=str(exc))
                return f"Error fetching headlines: {exc}"

        return get_top_headlines
