from collections import Counter
from datetime import datetime
from langchain.tools import tool
from app.tools.news_client import NewsClient
from app.utils.exceptions import NewsAPIError
from app.utils.logger import get_logger
import re

logger = get_logger(__name__)

# Common words to ignore when extracting trending topics
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "has", "have",
    "be", "been", "being", "that", "this", "it", "its", "as", "up", "he",
    "she", "they", "we", "you", "i", "my", "your", "his", "her", "our",
    "after", "before", "about", "over", "into", "out", "new", "says", "said",
    "will", "can", "than", "more", "also", "after", "first", "their", "what",
}


def _extract_keywords(articles: list) -> list:
    word_count: Counter = Counter()
    for article in articles:
        text = f"{article.get('title', '')} {article.get('description', '') or ''}"
        words = re.findall(r'\b[A-Z][a-zA-Z]{3,}\b', text)
        for word in words:
            if word.lower() not in STOP_WORDS:
                word_count[word] += 1
    return word_count.most_common(10)


class TrendingTopicsTool:
    def __init__(self, client: NewsClient) -> None:
        self._client = client

    def as_tool(self):
        client = self._client

        @tool
        async def get_trending_topics(country: str = "us") -> str:
            """Identify the top trending topics and keywords from today's news.
            Analyzes headlines to surface what subjects are appearing most frequently.
            Use for queries like 'What's trending today?', 'What are people talking about?',
            'What are the hot topics right now?'"""
            try:
                data = await client.get("/top-headlines", {
                    "country": country.lower(),
                    "pageSize": 100,
                })
                articles = data.get("articles", [])
                if not articles:
                    return "No trending topics found at the moment."

                keywords = _extract_keywords(articles)
                lines = [
                    f"🔥 Trending Topics Right Now ({country.upper()}) "
                    f"— {datetime.utcnow().strftime('%b %d, %Y')}\n"
                    f"Analyzed {len(articles)} articles\n"
                ]
                for rank, (word, count) in enumerate(keywords, 1):
                    bar = "█" * min(count, 10)
                    lines.append(f"  {rank:>2}. {word:<20} {bar} ({count} mentions)")

                return "\n".join(lines)
            except NewsAPIError as exc:
                logger.error("trending_topics_error", error=str(exc))
                return f"Error fetching trending topics: {exc}"

        return get_trending_topics
