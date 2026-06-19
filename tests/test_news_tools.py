import pytest
from unittest.mock import AsyncMock
from app.tools.news_client import NewsClient
from app.tools.top_headlines import TopHeadlinesTool
from app.tools.search_news import SearchNewsTool
from app.tools.category_news import CategoryNewsTool
from app.tools.trending_topics import TrendingTopicsTool
from app.utils.exceptions import NewsAPIError

MOCK_ARTICLES = [
    {
        "title": "AI Breakthrough in 2026",
        "source": {"name": "TechCrunch"},
        "publishedAt": "2026-06-19T08:00:00Z",
        "description": "Researchers announce a major leap in artificial intelligence capabilities.",
        "url": "https://techcrunch.com/ai-2026",
    },
    {
        "title": "Stock Markets Hit Record High",
        "source": {"name": "Reuters"},
        "publishedAt": "2026-06-19T07:30:00Z",
        "description": "Global markets surge on positive economic data.",
        "url": "https://reuters.com/markets-2026",
    },
]

MOCK_RESPONSE = {"status": "ok", "totalResults": 2, "articles": MOCK_ARTICLES}


@pytest.mark.asyncio
async def test_top_headlines_success():
    client = AsyncMock(spec=NewsClient)
    client.get.return_value = MOCK_RESPONSE

    tool = TopHeadlinesTool(client).as_tool()
    result = await tool.ainvoke({"country": "us"})

    assert "AI Breakthrough" in result
    assert "TechCrunch" in result
    assert "Top Headlines" in result


@pytest.mark.asyncio
async def test_top_headlines_no_articles():
    client = AsyncMock(spec=NewsClient)
    client.get.return_value = {"status": "ok", "totalResults": 0, "articles": []}

    tool = TopHeadlinesTool(client).as_tool()
    result = await tool.ainvoke({"country": "xx"})

    assert "No news found" in result


@pytest.mark.asyncio
async def test_search_news_success():
    client = AsyncMock(spec=NewsClient)
    client.get.return_value = MOCK_RESPONSE

    tool = SearchNewsTool(client).as_tool()
    result = await tool.ainvoke({"query": "artificial intelligence", "days": 1})

    assert "artificial intelligence" in result.lower() or "News Search" in result
    assert "TechCrunch" in result


@pytest.mark.asyncio
async def test_category_news_invalid_category():
    client = AsyncMock(spec=NewsClient)
    tool = CategoryNewsTool(client).as_tool()
    result = await tool.ainvoke({"category": "invalid_cat"})

    assert "Invalid category" in result


@pytest.mark.asyncio
async def test_category_news_success():
    client = AsyncMock(spec=NewsClient)
    client.get.return_value = MOCK_RESPONSE

    tool = CategoryNewsTool(client).as_tool()
    result = await tool.ainvoke({"category": "technology"})

    assert "Technology News" in result


@pytest.mark.asyncio
async def test_trending_topics():
    client = AsyncMock(spec=NewsClient)
    client.get.return_value = {
        "status": "ok",
        "totalResults": 2,
        "articles": MOCK_ARTICLES * 5,
    }
    tool = TrendingTopicsTool(client).as_tool()
    result = await tool.ainvoke({"country": "us"})

    assert "Trending Topics" in result


@pytest.mark.asyncio
async def test_news_client_api_error():
    client = AsyncMock(spec=NewsClient)
    client.get.side_effect = NewsAPIError("Rate limit exceeded", status_code=429)

    tool = TopHeadlinesTool(client).as_tool()
    result = await tool.ainvoke({"country": "us"})

    assert "Error" in result
