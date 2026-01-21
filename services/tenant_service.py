import secrets
from pymongo.errors import DuplicateKeyError


class TenantService:
    def __init__(self, repo, settings):
        self.repo = repo
        self.settings = settings
        self._alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"

    def _generate_code(self) -> str:
        return "".join(secrets.choice(self._alphabet) for _ in range(6))

    def _default_config(self) -> dict:
        return {
            "layout": self.settings.DEFAULT_LAYOUT,
            "refresh_seconds": self.settings.DEFAULT_REFRESH_SECONDS,
            "swap_seconds": self.settings.DEFAULT_SWAP_SECONDS,
            "menu_mode": "menuAndImage",
            "show_youtube": False,
            "youtube_url": None,
            "show_weather": False,
            "weather_lang": "es",
            "weather_lat": None,
            "weather_lon": None,
            "theme": self.settings.DEFAULT_THEME,
            "board_header_text": self.settings.DEFAULT_BOARD_HEADER_TEXT,
            "stops": [],
            "line_arrive_default": None,
            "timezone": None,
        }

    async def get_tenant_and_config(self, code: str):
        tenant = await self.repo.get_by_code(code)
        if not tenant or not tenant.is_active:
            return None, None
        config = await self.repo.get_config(tenant.id)
        if not config:
            config = await self.repo.create_default_config(tenant.id, self._default_config())
        return tenant, config

    async def get_tenant_by_id(self, tenant_id: str):
        return await self.repo.get_by_id(tenant_id)

    async def get_config_for_tenant(self, tenant_id: str):
        return await self.repo.get_config(tenant_id)

    async def create_tenant(self, name: str):
        for _ in range(10):
            code = self._generate_code()
            try:
                tenant = await self.repo.create_tenant(name, code)
                await self.repo.create_default_config(tenant.id, self._default_config())
                return tenant
            except DuplicateKeyError:
                continue
        raise RuntimeError("Could not generate unique short code")
