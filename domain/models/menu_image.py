from datetime import datetime
from pydantic import BaseModel


class MenuImage(BaseModel):
    id: str
    tenant_id: str
    url: str
    caption: str | None
    is_active: bool
    created_at: datetime
