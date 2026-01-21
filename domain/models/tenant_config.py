from pydantic import BaseModel, model_validator


class TenantConfig(BaseModel):
    tenant_id: str
    layout: str
    refresh_seconds: int
    swap_seconds: int
    menu_mode: str
    show_youtube: bool = False
    youtube_url: str | None = None
    show_weather: bool = False
    weather_lang: str = "es"
    weather_lat: float | None = None
    weather_lon: float | None = None
    theme: str
    board_header_text: str
    stops: list[str]
    line_arrive_default: str | None = None
    timezone: str | None = None

    @model_validator(mode="after")
    def _validate_weather(self):
        if self.show_weather:
            if self.weather_lat is None or self.weather_lon is None:
                raise ValueError("weather_lat and weather_lon are required when show_weather is true")
            if not (self.weather_lang or "").strip():
                raise ValueError("weather_lang is required when show_weather is true")
        return self
