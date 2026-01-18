from datetime import datetime
from zoneinfo import ZoneInfo


class MenuService:
    def __init__(self, menu_repo, tenant_repo):
        self.menu_repo = menu_repo
        self.tenant_repo = tenant_repo

    def _today_str(self, timezone_name: str | None) -> str:
        if timezone_name:
            tz = ZoneInfo(timezone_name)
            return datetime.now(tz).strftime("%Y-%m-%d")
        return datetime.now().strftime("%Y-%m-%d")

    async def get_menu_with_image(self, tenant_id: str, timezone_name: str | None):
        date_str = self._today_str(timezone_name)
        menu = await self.menu_repo.get_menu_for_date(tenant_id, date_str)
        image = await self.menu_repo.get_active_image(tenant_id)
        return menu, image

    async def update_menu_text(
        self, tenant_id: str, text_raw: str, title: str, timezone_name: str | None
    ):
        date_str = self._today_str(timezone_name)
        return await self.menu_repo.upsert_menu(
            tenant_id, date_str, title, text_raw, None, None
        )

    async def publish_today(self, tenant_id: str, timezone_name: str | None):
        date_str = self._today_str(timezone_name)
        return await self.menu_repo.publish_menu(tenant_id, date_str)

    async def get_status(self, tenant_id: str, timezone_name: str | None):
        date_str = self._today_str(timezone_name)
        return await self.menu_repo.get_menu_for_date(tenant_id, date_str)

    async def update_featured_image(self, tenant_id: str, url: str, caption: str | None):
        return await self.menu_repo.upsert_image(tenant_id, url, caption)
