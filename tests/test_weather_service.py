import pytest

from domain.models.tenant_config import TenantConfig
from infrastructure.clients.openweather_client import OpenWeatherClientError
from schemas.openweather_schemas import OpenWeatherResponse
from services.weather_service import WeatherService


class StubSettings:
    def __init__(self, refresh_seconds: int):
        self.WEATHER_REFRESH_SECONDS = refresh_seconds


class StubOpenWeatherClient:
    def __init__(self, response: OpenWeatherResponse):
        self.response = response
        self.calls = 0

    async def get_current_weather(self, lat: float, lon: float, lang: str) -> OpenWeatherResponse:
        self.calls += 1
        return self.response


class FlakyOpenWeatherClient:
    def __init__(self, response: OpenWeatherResponse):
        self.response = response
        self.calls = 0

    async def get_current_weather(self, lat: float, lon: float, lang: str) -> OpenWeatherResponse:
        self.calls += 1
        if self.calls > 1:
            raise OpenWeatherClientError("boom")
        return self.response


def build_sample_response() -> OpenWeatherResponse:
    payload = {
        "coord": {"lon": -3.7, "lat": 40.4},
        "weather": [
            {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}
        ],
        "main": {
            "temp": 17.8,
            "feels_like": 17.9,
            "temp_min": 16.0,
            "temp_max": 19.0,
            "humidity": 90,
            "pressure": 1012,
        },
        "wind": {"speed": 3.2, "deg": 120},
        "clouds": {"all": 0},
        "dt": 1700000000,
        "timezone": 3600,
        "name": "Madrid",
        "cod": 200,
        "sys": {"sunrise": 1699990000, "sunset": 1700030000},
    }
    return OpenWeatherResponse.model_validate(payload)


def build_sample_config() -> TenantConfig:
    return TenantConfig(
        tenant_id="tenant-1",
        layout="horizontal",
        refresh_seconds=10,
        swap_seconds=10,
        menu_mode="menuAndImage",
        show_youtube=False,
        youtube_url=None,
        show_weather=True,
        weather_lang="es",
        weather_lat=40.4,
        weather_lon=-3.7,
        theme="purple",
        board_header_text="Header",
        stops=["100"],
        line_arrive_default="0",
        timezone=None,
    )


def test_openweather_parsing():
    response = build_sample_response()
    dto = WeatherService._to_widget_dto(response)
    assert dto.temp_c == 17.8
    assert dto.feels_like_c == 17.9
    assert dto.description == "clear sky"
    assert dto.icon_code == "01d"
    assert dto.is_night is False


@pytest.mark.anyio
async def test_weather_cache_hits():
    response = build_sample_response()
    client = StubOpenWeatherClient(response)
    settings = StubSettings(refresh_seconds=600)
    service = WeatherService(client, settings)
    config = build_sample_config()

    first = await service.get_weather("ABC123", config)
    second = await service.get_weather("ABC123", config)

    assert client.calls == 1
    assert first.updated_at == second.updated_at


@pytest.mark.anyio
async def test_weather_stale_on_error():
    response = build_sample_response()
    client = FlakyOpenWeatherClient(response)
    settings = StubSettings(refresh_seconds=0)
    service = WeatherService(client, settings)
    config = build_sample_config()

    first = await service.get_weather("ABC123", config)
    second = await service.get_weather("ABC123", config)

    assert client.calls == 2
    assert first.stale is False
    assert second.stale is True
