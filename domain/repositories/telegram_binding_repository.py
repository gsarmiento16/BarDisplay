from typing import Protocol
from domain.models.telegram_binding import TelegramBinding


class TelegramBindingRepository(Protocol):
    async def get_by_chat_id(self, chat_id: int) -> TelegramBinding | None:
        ...

    async def upsert_binding(
        self, tenant_id: str, chat_id: int, username: str | None
    ) -> TelegramBinding:
        ...
