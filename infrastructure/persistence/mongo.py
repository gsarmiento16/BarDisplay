from motor.motor_asyncio import AsyncIOMotorClient


class MongoManager:
    def __init__(self, uri: str, db_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

    async def init_indexes(self) -> None:
        await self.db["tenants"].create_index("short_code", unique=True)
        await self.db["tenant_configs"].create_index("tenant_id")
        await self.db["daily_menus"].create_index(
            [("tenant_id", 1), ("valid_for_date", 1)], unique=True
        )
        await self.db["telegram_bindings"].create_index("telegram_chat_id", unique=True)
        await self.db["telegram_bindings"].create_index("tenant_id")
