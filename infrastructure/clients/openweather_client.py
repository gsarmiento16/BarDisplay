import logging
from pydantic import ValidationError

from infrastructure.clients.exceptions import HttpClientError
from schemas.openweather_schemas import OpenWeatherResponse

logger = logging.getLogger("openweather")


class OpenWeatherClientError(Exception):
    pass


class OpenWeatherClient:
    def __init__(self, http_client, settings):
        self.http_client = http_client
        self.settings = settings

    async def get_current_weather(self, lat: float, lon: float, lang: str) -> OpenWeatherResponse:
        params = {
            "appid": self.settings.OPENWEATHER_API_KEY,
            "units": self.settings.OPENWEATHER_UNITS,
            "lang": lang,
            "lat": lat,
            "lon": lon,
        }
        try:
            response = await self.http_client.get("/data/2.5/weather", params=params)
        except HttpClientError as exc:
            logger.warning("OpenWeather request failed: %s", exc)
            raise OpenWeatherClientError(str(exc)) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            logger.warning("OpenWeather returned invalid JSON")
            raise OpenWeatherClientError("Invalid JSON response") from exc

        try:
            return OpenWeatherResponse.model_validate(payload)
        except ValidationError as exc:
            logger.warning("OpenWeather response schema error: %s", exc)
            raise OpenWeatherClientError("Invalid weather response") from exc
