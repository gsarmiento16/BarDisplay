from pydantic import BaseModel


class OpenWeatherCoord(BaseModel):
    lon: float
    lat: float


class OpenWeatherWeatherItem(BaseModel):
    id: int
    main: str
    description: str
    icon: str


class OpenWeatherMain(BaseModel):
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    humidity: int
    pressure: int


class OpenWeatherWind(BaseModel):
    speed: float
    deg: int | None = None
    gust: float | None = None


class OpenWeatherSys(BaseModel):
    sunrise: int | None = None
    sunset: int | None = None


class OpenWeatherResponse(BaseModel):
    coord: OpenWeatherCoord
    weather: list[OpenWeatherWeatherItem]
    main: OpenWeatherMain
    wind: OpenWeatherWind | None = None
    clouds: dict | None = None
    dt: int
    timezone: int
    name: str | None = None
    cod: int
    sys: OpenWeatherSys | None = None
