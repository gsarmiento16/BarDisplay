from datetime import datetime
from pydantic import BaseModel


class TelegramBinding(BaseModel):
    id: str
    tenant_id: str
    telegram_chat_id: int
    linked_at: datetime
    linked_by_username: str | None
    is_active: bool
