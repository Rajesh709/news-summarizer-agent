from datetime import datetime
from langchain.tools import tool
from app.tools.news_client import NewsClient
from app.tools.top_headlines import _format_articles
from app.utils.exceptions import NewsAPIError, NoNewsFoundError
from app.utils.logger import get_logger

logger = get_logger(__name__)

COUNTRY_CODES = {
    "india": "in", "united states": "us", "usa": "us", "us": "us",
    "uk": "gb", "united kingdom": "gb", "britain": "gb",
    "australia": "au", "canada": "ca", "germany": "de",
    "france": "fr", "japan": "jp", "china": "cn", "brazil": "br",
    "russia": "ru", "south africa": "za", "uae": "ae",
    "singapore": "sg", "pakistan": "pk", "bangladesh": "bd",
}

COUNTRY_FLAGS = {
    "in": "🇮🇳", "us": "🇺🇸", "gb": "🇬🇧", "au": "🇦🇺", "ca": "🇨🇦",
    "de": "🇩🇪", "fr": "🇫🇷", "jp": "🇯🇵", "cn": "🇨🇳", "br": "🇧🇷",
    "ru": "🇷🇺", "za": "🇿🇦", "ae": "🇦🇪", "sg": "🇸🇬",
}


class CountryNewsTool:
    def __init__(self, client: NewsClient) -> None:
        self._client = client

    def as_tool(self):
        client = self._client

        @tool
        async def get_country_news(country: str) -> str:
            """Get top news headlines for a specific country.
            Accepts country names like 'India', 'UK', 'Australia', 'Germany'
            or 2-letter codes like 'in', 'gb', 'au'.
            Use for country-specific queries like 'News from India today',
            'What's happening in the UK?', 'Japan latest news'."""
            country_lower = country.lower().strip()
            code = COUNTRY_CODES.get(country_lower, country_lower[:2])
            flag = COUNTRY_FLAGS.get(code, "🌍")

            try:
                data = await client.get("/top-headlines", {
                    "country": code,
                    "pageSize": 5,
                })
                articles = data.get("articles", [])
                if not articles:
                    raise NoNewsFoundError(f"No news found for country '{country}'.")

                total = data.get("totalResults", 0)
                header = (
                    f"{flag} **Top News from {country.title()}** "
                    f"— {datetime.utcnow().strftime('%b %d, %Y')}\n"
                    f"📊 {total} articles available\n\n"
                )
                return header + _format_articles(articles, 5)
            except NoNewsFoundError as exc:
                return f"No news found: {exc}"
            except NewsAPIError as exc:
                logger.error("country_news_error", country=country, error=str(exc))
                return f"Error fetching news for '{country}': {exc}"

        return get_country_news
