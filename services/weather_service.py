from dataclasses import dataclass
from datetime import datetime, timezone
import time

from schemas.api_schemas import WeatherWidgetDto
from schemas.openweather_schemas import OpenWeatherResponse
from infrastructure.clients.openweather_client import OpenWeatherClient, OpenWeatherClientError


@dataclass
class WeatherCacheEntry:
    dto: WeatherWidgetDto
    fetched_at: float
    lat: float
    lon: float
    lang: str


class WeatherService:
    def __init__(self, client: OpenWeatherClient, settings):
        self.client = client
        self.settings = settings
        self._cache: dict[str, WeatherCacheEntry] = {}

    async def get_weather(self, tenant_code: str, config) -> WeatherWidgetDto | None:
        if not config.show_weather:
            return None

        cache_entry = self._cache.get(tenant_code)
        coords_match = False
        if cache_entry:
            coords_match = (
                cache_entry.lat == config.weather_lat
                and cache_entry.lon == config.weather_lon
                and cache_entry.lang == config.weather_lang
            )
        now = time.monotonic()
        if (
            cache_entry
            and coords_match
            and (now - cache_entry.fetched_at) < self.settings.WEATHER_REFRESH_SECONDS
        ):
            return cache_entry.dto

        try:
            response = await self.client.get_current_weather(
                config.weather_lat,
                config.weather_lon,
                config.weather_lang,
            )
            dto = self._to_widget_dto(response)
            self._cache[tenant_code] = WeatherCacheEntry(
                dto=dto,
                fetched_at=now,
                lat=config.weather_lat,
                lon=config.weather_lon,
                lang=config.weather_lang,
            )
            return dto
        except OpenWeatherClientError:
            if cache_entry and coords_match:
                return cache_entry.dto.model_copy(update={"stale": True})
            raise

    @staticmethod
    def _to_widget_dto(response: OpenWeatherResponse) -> WeatherWidgetDto:
        primary = response.weather[0] if response.weather else None
        icon_code = primary.icon if primary else ""
        description = primary.description if primary else ""

        is_night = icon_code.endswith("n")
        if response.sys and response.sys.sunrise and response.sys.sunset:
            is_night = is_night or not (response.sys.sunrise <= response.dt <= response.sys.sunset)

        updated_at = datetime.fromtimestamp(response.dt, tz=timezone.utc)
        wind_mps = response.wind.speed if response.wind else None

        return WeatherWidgetDto(
            temp_c=response.main.temp,
            feels_like_c=response.main.feels_like,
            humidity_pct=response.main.humidity,
            wind_mps=wind_mps,
            description=description,
            icon_code=icon_code,
            is_night=is_night,
            updated_at=updated_at,
            stale=False,
        )
