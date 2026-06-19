import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import get_settings
from app.utils.exceptions import NewsAPIError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NewsClient:
    """Async HTTP client for the NewsAPI."""

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.news_api_key
        self._base_url = settings.news_api_base_url
        self._client = httpx.AsyncClient(timeout=15.0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(httpx.TimeoutException),
    )
    async def get(self, endpoint: str, params: dict) -> dict:
        params["apiKey"] = self._api_key
        url = f"{self._base_url}{endpoint}"
        logger.debug("news_api_request", url=url)

        response = await self._client.get(url, params=params)

        if response.status_code == 401:
            raise NewsAPIError("Invalid NewsAPI key.", status_code=401)
        if response.status_code == 429:
            raise NewsAPIError("NewsAPI rate limit exceeded.", status_code=429)
        if response.status_code != 200:
            raise NewsAPIError(f"NewsAPI error: {response.text}", status_code=response.status_code)

        data = response.json()
        if data.get("status") == "error":
            raise NewsAPIError(data.get("message", "Unknown NewsAPI error"))

        return data

    async def close(self) -> None:
        await self._client.aclose()
