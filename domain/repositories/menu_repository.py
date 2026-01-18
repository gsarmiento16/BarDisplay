from datetime import datetime
from typing import Protocol
from domain.models.daily_menu import DailyMenu
from domain.models.menu_image import MenuImage


class MenuRepository(Protocol):
    async def get_menu_for_date(self, tenant_id: str, date_str: str) -> DailyMenu | None:
        ...

    async def upsert_menu(
        self,
        tenant_id: str,
        date_str: str,
        title: str,
        text_raw: str,
        sections: dict | None,
        published_at: datetime | None,
    ) -> DailyMenu:
        ...

    async def publish_menu(self, tenant_id: str, date_str: str) -> DailyMenu | None:
        ...

    async def get_active_image(self, tenant_id: str) -> MenuImage | None:
        ...

    async def upsert_image(self, tenant_id: str, url: str, caption: str | None) -> MenuImage:
        ...
