from datetime import datetime
from pydantic import BaseModel


class DailyMenu(BaseModel):
    id: str
    tenant_id: str
    valid_for_date: str
    title: str
    sections: dict | None
    text_raw: str | None
    published_at: datetime | None
    updated_at: datetime
