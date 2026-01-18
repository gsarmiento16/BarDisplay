from datetime import datetime, timezone
from bson import ObjectId
from domain.models.daily_menu import DailyMenu
from domain.models.menu_image import MenuImage


class MenuRepositoryMongo:
    def __init__(self, db):
        self._menus = db["daily_menus"]
        self._images = db["menu_images"]

    async def get_menu_for_date(self, tenant_id: str, date_str: str) -> DailyMenu | None:
        doc = await self._menus.find_one({"tenant_id": ObjectId(tenant_id), "valid_for_date": date_str})
        if not doc:
            return None
        return DailyMenu(
            id=str(doc["_id"]),
            tenant_id=str(doc["tenant_id"]),
            valid_for_date=doc["valid_for_date"],
            title=doc.get("title", "Menu of the day"),
            sections=doc.get("sections"),
            text_raw=doc.get("text_raw"),
            published_at=doc.get("published_at"),
            updated_at=doc["updated_at"],
        )

    async def upsert_menu(
        self,
        tenant_id: str,
        date_str: str,
        title: str,
        text_raw: str,
        sections: dict | None,
        published_at: datetime | None,
    ) -> DailyMenu:
        now = datetime.now(timezone.utc)
        await self._menus.update_one(
            {"tenant_id": ObjectId(tenant_id), "valid_for_date": date_str},
            {
                "$set": {
                    "title": title,
                    "text_raw": text_raw,
                    "sections": sections,
                    "updated_at": now,
                },
                "$setOnInsert": {"published_at": published_at},
            },
            upsert=True,
        )
        doc = await self._menus.find_one({"tenant_id": ObjectId(tenant_id), "valid_for_date": date_str})
        return DailyMenu(
            id=str(doc["_id"]),
            tenant_id=str(doc["tenant_id"]),
            valid_for_date=doc["valid_for_date"],
            title=doc.get("title", "Menu of the day"),
            sections=doc.get("sections"),
            text_raw=doc.get("text_raw"),
            published_at=doc.get("published_at"),
            updated_at=doc["updated_at"],
        )

    async def publish_menu(self, tenant_id: str, date_str: str) -> DailyMenu | None:
        now = datetime.now(timezone.utc)
        await self._menus.update_one(
            {"tenant_id": ObjectId(tenant_id), "valid_for_date": date_str},
            {"$set": {"published_at": now, "updated_at": now}},
            upsert=True,
        )
        doc = await self._menus.find_one({"tenant_id": ObjectId(tenant_id), "valid_for_date": date_str})
        if not doc:
            return None
        return DailyMenu(
            id=str(doc["_id"]),
            tenant_id=str(doc["tenant_id"]),
            valid_for_date=doc["valid_for_date"],
            title=doc.get("title", "Menu of the day"),
            sections=doc.get("sections"),
            text_raw=doc.get("text_raw"),
            published_at=doc.get("published_at"),
            updated_at=doc["updated_at"],
        )

    async def get_active_image(self, tenant_id: str) -> MenuImage | None:
        doc = await self._images.find_one(
            {"tenant_id": ObjectId(tenant_id), "is_active": True},
            sort=[("created_at", -1)],
        )
        if not doc:
            return None
        return MenuImage(
            id=str(doc["_id"]),
            tenant_id=str(doc["tenant_id"]),
            url=doc["url"],
            caption=doc.get("caption"),
            is_active=doc.get("is_active", True),
            created_at=doc["created_at"],
        )

    async def upsert_image(self, tenant_id: str, url: str, caption: str | None) -> MenuImage:
        now = datetime.now(timezone.utc)
        await self._images.update_many(
            {"tenant_id": ObjectId(tenant_id), "is_active": True},
            {"$set": {"is_active": False}},
        )
        doc = {
            "tenant_id": ObjectId(tenant_id),
            "url": url,
            "caption": caption,
            "is_active": True,
            "created_at": now,
        }
        result = await self._images.insert_one(doc)
        return MenuImage(
            id=str(result.inserted_id),
            tenant_id=tenant_id,
            url=url,
            caption=caption,
            is_active=True,
            created_at=now,
        )
