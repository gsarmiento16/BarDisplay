from datetime import datetime
from pydantic import BaseModel


class Tenant(BaseModel):
    id: str
    name: str
    short_code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
