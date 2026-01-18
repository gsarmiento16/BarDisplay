import httpx
from infrastructure.clients.exceptions import HttpClientError, HttpClientResponseError, HttpClientTimeout


class HttpClient:
    def __init__(self, base_url: str, timeout_seconds: int, default_headers: dict | None = None):
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout_seconds,
            headers=default_headers,
        )

    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        try:
            response = await self._client.request(method, url, **kwargs)
        except httpx.TimeoutException as exc:
            raise HttpClientTimeout(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise HttpClientError(str(exc)) from exc

        if response.status_code >= 400:
            raise HttpClientResponseError(response.status_code, response.text)

        return response

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("DELETE", url, **kwargs)

    async def close(self) -> None:
        await self._client.aclose()
