from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TenantConfigResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    tenant_name: str = Field(serialization_alias="tenantName")
    layout: str
    refresh_seconds: int = Field(serialization_alias="refreshSeconds")
    swap_seconds: int = Field(serialization_alias="swapSeconds")
    menu_mode: str = Field(serialization_alias="menuMode")
    show_youtube: bool = Field(serialization_alias="showYoutube")
    youtube_url: str | None = Field(serialization_alias="youtubeUrl")
    show_weather: bool = Field(serialization_alias="showWeather")
    weather_lang: str | None = Field(serialization_alias="weatherLang")
    weather_lat: float | None = Field(serialization_alias="weatherLat")
    weather_lon: float | None = Field(serialization_alias="weatherLon")
    weather_refresh_seconds: int = Field(serialization_alias="weatherRefreshSeconds")
    theme: str
    board_header_text: str = Field(serialization_alias="boardHeaderText")
    stops: list[str]


class ArrivalItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    stop: str
    line: str
    destination: str
    eta_seconds: int = Field(serialization_alias="etaSeconds")
    eta_minutes: int = Field(serialization_alias="etaMinutes")


class ArrivalsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    updated_at: datetime = Field(serialization_alias="updatedAt")
    items: list[ArrivalItem]


class MenuResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str
    sections: dict | None
    text_raw: str = Field(serialization_alias="textRaw")
    featured_image_url: str | None = Field(serialization_alias="featuredImageUrl")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class AdminCreateTenantRequest(BaseModel):
    name: str


class AdminCreateTenantResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str
    tenant_id: str = Field(serialization_alias="tenantId")
    url: str


class WeatherWidgetDto(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    temp_c: float = Field(serialization_alias="tempC")
    feels_like_c: float = Field(serialization_alias="feelsLikeC")
    humidity_pct: int = Field(serialization_alias="humidityPct")
    wind_mps: float | None = Field(serialization_alias="windMps")
    description: str
    icon_code: str = Field(serialization_alias="iconCode")
    is_night: bool = Field(serialization_alias="isNight")
    updated_at: datetime = Field(serialization_alias="updatedAt")
    stale: bool = False
