from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class EmtGeometry(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: str
    coordinates: list[float]


class EmtArriveItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    line: str
    stop: str
    isHead: str | bool
    destination: str
    deviation: int
    bus: int | None = None
    geometry: EmtGeometry | None = None
    estimateArrive: int
    DistanceBus: int | None = None
    positionTypeBus: str | None = None


class EmtDataItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    Arrive: list[EmtArriveItem] = Field(alias="Arrive")
    StopInfo: list[Any] = Field(default_factory=list, alias="StopInfo")
    ExtraInfo: list[Any] = Field(default_factory=list, alias="ExtraInfo")
    Incident: dict[str, Any] = Field(default_factory=dict, alias="Incident")


class EmtArrivalResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    code: str
    description: str
    datetime: datetime
    data: list[EmtDataItem]
