from datetime import datetime, timezone
from bson import ObjectId
from domain.models.telegram_binding import TelegramBinding


class TelegramBindingRepositoryMongo:
    def __init__(self, db):
        self._bindings = db["telegram_bindings"]

    async def get_by_chat_id(self, chat_id: int) -> TelegramBinding | None:
        doc = await self._bindings.find_one({"telegram_chat_id": chat_id})
        if not doc:
            return None
        return TelegramBinding(
            id=str(doc["_id"]),
            tenant_id=str(doc["tenant_id"]),
            telegram_chat_id=doc["telegram_chat_id"],
            linked_at=doc["linked_at"],
            linked_by_username=doc.get("linked_by_username"),
            is_active=doc.get("is_active", True),
        )

    async def upsert_binding(
        self, tenant_id: str, chat_id: int, username: str | None
    ) -> TelegramBinding:
        now = datetime.now(timezone.utc)
        await self._bindings.update_one(
            {"telegram_chat_id": chat_id},
            {
                "$set": {
                    "tenant_id": ObjectId(tenant_id),
                    "telegram_chat_id": chat_id,
                    "linked_at": now,
                    "linked_by_username": username,
                    "is_active": True,
                }
            },
            upsert=True,
        )
        doc = await self._bindings.find_one({"telegram_chat_id": chat_id})
        return TelegramBinding(
            id=str(doc["_id"]),
            tenant_id=str(doc["tenant_id"]),
            telegram_chat_id=doc["telegram_chat_id"],
            linked_at=doc["linked_at"],
            linked_by_username=doc.get("linked_by_username"),
            is_active=doc.get("is_active", True),
        )
