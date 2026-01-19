import asyncio
import logging
import math
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Header, HTTPException

from app.dependencies import get_emt_service, get_menu_service, get_settings, get_tenant_service
from app.settings import Settings
from schemas.api_schemas import (
    AdminCreateTenantRequest,
    AdminCreateTenantResponse,
    ArrivalItem,
    ArrivalsResponse,
    MenuResponse,
    TenantConfigResponse,
)
from services.emt_madrid_service import EmtMadridService
from services.menu_service import MenuService
from services.tenant_config_utils import normalize_menu_mode
from services.tenant_service import TenantService
from services.youtube_embed import build_youtube_embed_url

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/api/tenants/{code}/config", response_model=TenantConfigResponse)
async def get_tenant_config(
    code: str,
    tenant_service: TenantService = Depends(get_tenant_service),
) -> TenantConfigResponse:
    tenant, config = await tenant_service.get_tenant_and_config(code)
    if not tenant or not config:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if config.show_youtube and not (config.youtube_url or "").strip():
        raise HTTPException(
            status_code=400, detail="youtubeUrl is required when showYoutube is true"
        )

    if config.show_youtube and config.youtube_url:
        if not build_youtube_embed_url(config.youtube_url):
            logger.warning("Invalid YouTube URL for tenant %s: %s", tenant.id, config.youtube_url)

    return TenantConfigResponse(
        tenant_name=tenant.name,
        layout=config.layout,
        refresh_seconds=config.refresh_seconds,
        swap_seconds=config.swap_seconds,
        menu_mode=normalize_menu_mode(config),
        show_youtube=config.show_youtube,
        youtube_url=config.youtube_url,
        theme=config.theme,
        board_header_text=config.board_header_text,
        stops=config.stops,
    )


@router.get("/api/tenants/{code}/arrivals", response_model=ArrivalsResponse)
async def get_arrivals(
    code: str,
    tenant_service: TenantService = Depends(get_tenant_service),
    emt_service: EmtMadridService = Depends(get_emt_service),
) -> ArrivalsResponse:
    tenant, config = await tenant_service.get_tenant_and_config(code)
    if not tenant or not config:
        raise HTTPException(status_code=404, detail="Tenant not found")

    line_default = config.line_arrive_default or "0"
    tasks = [emt_service.get_arrival_bus(stop_id, line_default) for stop_id in config.stops]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    items: list[ArrivalItem] = []
    for response in responses:
        if isinstance(response, Exception):
            continue
        for data_item in response.data:
            for arrive in data_item.Arrive:
                eta_seconds = int(arrive.estimateArrive)
                if eta_seconds < 0:
                    continue
                items.append(
                    ArrivalItem(
                        stop=arrive.stop,
                        line=arrive.line,
                        destination=arrive.destination,
                        eta_seconds=eta_seconds,
                        eta_minutes=max(1, math.ceil(eta_seconds / 60)),
                    )
                )

    items.sort(key=lambda item: item.eta_seconds)
    return ArrivalsResponse(updated_at=datetime.now(timezone.utc), items=items)


@router.get("/api/tenants/{code}/menu", response_model=MenuResponse)
async def get_menu(
    code: str,
    tenant_service: TenantService = Depends(get_tenant_service),
    menu_service: MenuService = Depends(get_menu_service),
) -> MenuResponse:
    tenant, config = await tenant_service.get_tenant_and_config(code)
    if not tenant or not config:
        raise HTTPException(status_code=404, detail="Tenant not found")

    menu, image = await menu_service.get_menu_with_image(tenant.id, config.timezone)
    menu_title = menu.title if menu else "Menu of the day"
    text_raw = menu.text_raw if menu and menu.text_raw else ""
    sections = menu.sections if menu else None

    return MenuResponse(
        title=menu_title,
        sections=sections,
        text_raw=text_raw,
        featured_image_url=image.url if image else None,
        updated_at=(menu.updated_at if menu else datetime.now(timezone.utc)),
    )


@router.post("/api/admin/tenants", response_model=AdminCreateTenantResponse)
async def create_tenant(
    payload: AdminCreateTenantRequest,
    x_admin_secret: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
    tenant_service: TenantService = Depends(get_tenant_service),
) -> AdminCreateTenantResponse:
    if x_admin_secret != settings.ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    tenant = await tenant_service.create_tenant(payload.name)
    return AdminCreateTenantResponse(
        code=tenant.short_code,
        tenant_id=tenant.id,
        url=f"/t/{tenant.short_code}",
    )
