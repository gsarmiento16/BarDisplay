from functools import lru_cache
from fastapi import Depends, HTTPException, Request

from app.settings import Settings
from infrastructure.repositories.menu_repository_mongo import MenuRepositoryMongo
from infrastructure.repositories.telegram_binding_repository_mongo import TelegramBindingRepositoryMongo
from infrastructure.repositories.tenant_repository_mongo import TenantRepositoryMongo
from services.emt_madrid_service import EmtMadridService
from services.menu_service import MenuService
from services.telegram_service import TelegramService
from services.tenant_service import TenantService


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_tenant_repository(request: Request) -> TenantRepositoryMongo:
    return TenantRepositoryMongo(request.app.state.db)


def get_menu_repository(request: Request) -> MenuRepositoryMongo:
    return MenuRepositoryMongo(request.app.state.db)


def get_binding_repository(request: Request) -> TelegramBindingRepositoryMongo:
    return TelegramBindingRepositoryMongo(request.app.state.db)


def get_tenant_service(
    repo: TenantRepositoryMongo = Depends(get_tenant_repository),
    settings: Settings = Depends(get_settings),
) -> TenantService:
    return TenantService(repo, settings)


def get_menu_service(
    menu_repo: MenuRepositoryMongo = Depends(get_menu_repository),
    tenant_repo: TenantRepositoryMongo = Depends(get_tenant_repository),
) -> MenuService:
    return MenuService(menu_repo, tenant_repo)


def get_emt_service(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> EmtMadridService:
    client = request.app.state.http_client
    return EmtMadridService(client, settings)


def get_telegram_service(
    request: Request,
    settings: Settings = Depends(get_settings),
    tenant_repo: TenantRepositoryMongo = Depends(get_tenant_repository),
    menu_repo: MenuRepositoryMongo = Depends(get_menu_repository),
    binding_repo: TelegramBindingRepositoryMongo = Depends(get_binding_repository),
) -> TelegramService:
    client = request.app.state.telegram_client
    if client is None:
        raise HTTPException(status_code=503, detail="Telegram client not configured")
    tenant_service = TenantService(tenant_repo, settings)
    menu_service = MenuService(menu_repo, tenant_repo)
    return TelegramService(client, tenant_service, menu_service, binding_repo, settings)
