import pytest
from types import SimpleNamespace
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timezone

from services.tenant_service import TenantService
from domain.models.tenant import Tenant
from domain.models.tenant_config import TenantConfig


class CollisionRepo:
    def __init__(self):
        self.calls = 0

    async def get_by_code(self, code: str):
        return None

    async def get_by_id(self, tenant_id: str):
        return None

    async def get_config(self, tenant_id: str):
        return None

    async def create_default_config(self, tenant_id: str, defaults: dict):
        return TenantConfig(
            tenant_id=tenant_id,
            layout=defaults["layout"],
            refresh_seconds=defaults["refresh_seconds"],
            swap_seconds=defaults["swap_seconds"],
            menu_mode=defaults["menu_mode"],
            theme=defaults["theme"],
            board_header_text=defaults["board_header_text"],
            stops=defaults["stops"],
            line_arrive_default=defaults["line_arrive_default"],
            timezone=defaults["timezone"],
        )

    async def create_tenant(self, name: str, code: str):
        self.calls += 1
        if self.calls == 1:
            raise DuplicateKeyError("duplicate")
        return Tenant(
            id="tenant-1",
            name=name,
            short_code=code,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )


@pytest.mark.anyio
async def test_short_code_retries_on_collision():
    settings = SimpleNamespace(
        DEFAULT_LAYOUT="horizontal",
        DEFAULT_REFRESH_SECONDS=60,
        DEFAULT_SWAP_SECONDS=30,
        DEFAULT_THEME="purple",
        DEFAULT_BOARD_HEADER_TEXT="Bus arriving at nearby stops",
    )
    repo = CollisionRepo()
    service = TenantService(repo, settings)

    tenant = await service.create_tenant("Bar X")
    assert tenant.short_code
    assert repo.calls == 2
