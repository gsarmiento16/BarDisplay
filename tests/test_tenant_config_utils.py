from domain.models.tenant_config import TenantConfig
from services.tenant_config_utils import normalize_menu_mode


def test_normalize_menu_mode_for_youtube():
    config = TenantConfig(
        tenant_id="tenant-1",
        layout="horizontal",
        refresh_seconds=10,
        swap_seconds=15,
        menu_mode="menuAndImage",
        show_youtube=True,
        youtube_url="https://youtu.be/VIDEO123",
        theme="purple",
        board_header_text="Header",
        stops=[],
    )

    assert normalize_menu_mode(config) == "menuOnly"


def test_normalize_menu_mode_regular():
    config = TenantConfig(
        tenant_id="tenant-1",
        layout="horizontal",
        refresh_seconds=10,
        swap_seconds=15,
        menu_mode="menuAndImage",
        show_youtube=False,
        youtube_url=None,
        theme="purple",
        board_header_text="Header",
        stops=[],
    )

    assert normalize_menu_mode(config) == "menuAndImage"
