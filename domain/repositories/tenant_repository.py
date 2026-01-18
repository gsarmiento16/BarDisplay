from typing import Protocol
from domain.models.tenant import Tenant
from domain.models.tenant_config import TenantConfig


class TenantRepository(Protocol):
    async def get_by_code(self, code: str) -> Tenant | None:
        ...

    async def get_by_id(self, tenant_id: str) -> Tenant | None:
        ...

    async def create_tenant(self, name: str, code: str) -> Tenant:
        ...

    async def get_config(self, tenant_id: str) -> TenantConfig | None:
        ...

    async def create_default_config(self, tenant_id: str, defaults: dict) -> TenantConfig:
        ...
