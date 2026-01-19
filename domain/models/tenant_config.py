from pydantic import BaseModel


class TenantConfig(BaseModel):
    tenant_id: str
    layout: str
    refresh_seconds: int
    swap_seconds: int
    menu_mode: str
    show_youtube: bool = False
    youtube_url: str | None = None
    theme: str
    board_header_text: str
    stops: list[str]
    line_arrive_default: str | None = None
    timezone: str | None = None
