from datetime import datetime, timezone
from bson import ObjectId
from domain.models.tenant import Tenant
from domain.models.tenant_config import TenantConfig


class TenantRepositoryMongo:
    def __init__(self, db):
        self._tenants = db["tenants"]
        self._configs = db["tenant_configs"]

    async def get_by_code(self, code: str) -> Tenant | None:
        doc = await self._tenants.find_one({"short_code": code})
        if not doc:
            return None
        return Tenant(
            id=str(doc["_id"]),
            name=doc["name"],
            short_code=doc["short_code"],
            is_active=doc.get("is_active", True),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )

    async def get_by_id(self, tenant_id: str) -> Tenant | None:
        doc = await self._tenants.find_one({"_id": ObjectId(tenant_id)})
        if not doc:
            return None
        return Tenant(
            id=str(doc["_id"]),
            name=doc["name"],
            short_code=doc["short_code"],
            is_active=doc.get("is_active", True),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )

    async def create_tenant(self, name: str, code: str) -> Tenant:
        now = datetime.now(timezone.utc)
        doc = {
            "name": name,
            "short_code": code,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }
        result = await self._tenants.insert_one(doc)
        return Tenant(
            id=str(result.inserted_id),
            name=name,
            short_code=code,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    async def get_config(self, tenant_id: str) -> TenantConfig | None:
        doc = await self._configs.find_one({"tenant_id": ObjectId(tenant_id)})
        if not doc:
            return None
        return TenantConfig(
            tenant_id=str(doc["tenant_id"]),
            layout=doc["layout"],
            refresh_seconds=doc["refresh_seconds"],
            swap_seconds=doc["swap_seconds"],
            menu_mode=doc["menu_mode"],
            show_youtube=doc.get("show_youtube", False),
            youtube_url=doc.get("youtube_url"),
            show_weather=doc.get("show_weather", False),
            weather_lang=doc.get("weather_lang", "es"),
            weather_lat=doc.get("weather_lat"),
            weather_lon=doc.get("weather_lon"),
            theme=doc["theme"],
            board_header_text=doc["board_header_text"],
            stops=doc.get("stops", []),
            line_arrive_default=doc.get("line_arrive_default"),
            timezone=doc.get("timezone"),
        )

    async def create_default_config(self, tenant_id: str, defaults: dict) -> TenantConfig:
        now = datetime.now(timezone.utc)
        doc = {"tenant_id": ObjectId(tenant_id), **defaults, "updated_at": now}
        await self._configs.insert_one(doc)
        return TenantConfig(
            tenant_id=str(doc["tenant_id"]),
            layout=doc["layout"],
            refresh_seconds=doc["refresh_seconds"],
            swap_seconds=doc["swap_seconds"],
            menu_mode=doc["menu_mode"],
            show_youtube=doc.get("show_youtube", False),
            youtube_url=doc.get("youtube_url"),
            show_weather=doc.get("show_weather", False),
            weather_lang=doc.get("weather_lang", "es"),
            weather_lat=doc.get("weather_lat"),
            weather_lon=doc.get("weather_lon"),
            theme=doc["theme"],
            board_header_text=doc["board_header_text"],
            stops=doc.get("stops", []),
            line_arrive_default=doc.get("line_arrive_default"),
            timezone=doc.get("timezone"),
        )
