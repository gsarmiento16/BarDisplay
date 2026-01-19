from domain.models.tenant_config import TenantConfig


def normalize_menu_mode(config: TenantConfig) -> str:
    if config.show_youtube:
        return "menuOnly"
    return config.menu_mode
