import asyncio
from pathlib import Path
from services.menu_service import MenuService
from services.tenant_service import TenantService
from schemas.telegram_schemas import TelegramMessage, TelegramUpdate


class TelegramService:
    def __init__(self, client, tenant_service: TenantService, menu_service: MenuService, binding_repo, settings):
        self.client = client
        self.tenant_service = tenant_service
        self.menu_service = menu_service
        self.binding_repo = binding_repo
        self.settings = settings
        self.allowed_updates = {
            item.strip()
            for item in settings.TELEGRAM_ALLOWED_UPDATE_TYPES.split(",")
            if item.strip()
        }
        self.max_image_bytes = settings.TELEGRAM_MAX_IMAGE_MB * 1024 * 1024
        self._stop_event = asyncio.Event()

    async def handle_update(self, update: TelegramUpdate, background_tasks=None) -> None:
        if update.message and "message" not in self.allowed_updates:
            return
        if update.edited_message and "edited_message" not in self.allowed_updates:
            return

        message = update.message or update.edited_message
        if not message:
            return

        chat_id = message.chat.id
        text = message.text.strip() if message.text else None

        binding = await self.binding_repo.get_by_chat_id(chat_id)

        if text and text.startswith("/link"):
            await self._handle_link(message, text, binding)
            return

        if not binding or not binding.is_active:
            await self.client.send_message(chat_id, "Please link this chat with /link <TENANT_CODE> first.")
            return

        if text:
            await self._handle_text(message, text, binding)
            return

        if message.photo:
            if background_tasks:
                background_tasks.add_task(self._handle_photo, message, binding)
            else:
                await self._handle_photo(message, binding)

    async def _handle_link(self, message: TelegramMessage, text: str, binding) -> None:
        chat_id = message.chat.id
        parts = text.split()
        if len(parts) < 2:
            await self.client.send_message(chat_id, "Usage: /link <TENANT_CODE>")
            return

        code = parts[1].strip().upper()
        tenant, _ = await self.tenant_service.get_tenant_and_config(code)
        if not tenant:
            await self.client.send_message(chat_id, "Invalid tenant code.")
            return

        if binding and binding.tenant_id == tenant.id:
            await self.client.send_message(chat_id, "Already linked to this tenant.")
            return
        if binding and binding.tenant_id != tenant.id:
            await self.client.send_message(chat_id, "This chat is already linked to another tenant.")
            return

        username = message.from_.username if message.from_ else None
        await self.binding_repo.upsert_binding(tenant.id, chat_id, username)
        await self.client.send_message(
            chat_id, f"✅ Linked to tenant: {tenant.name}. You can now update the menu."
        )

    async def _handle_text(self, message: TelegramMessage, text: str, binding) -> None:
        chat_id = message.chat.id
        config = await self.tenant_service.get_config_for_tenant(binding.tenant_id)
        timezone_name = config.timezone if config else None

        if text.startswith("/menu"):
            payload = text[5:].strip()
            if not payload:
                await self.client.send_message(
                    chat_id,
                    "Send /menu <text> or just send a menu text message to update today.",
                )
                return
            await self.menu_service.update_menu_text(
                binding.tenant_id, payload, "Menu of the day", timezone_name
            )
            await self.client.send_message(chat_id, "📋 Menu updated ✅")
            return

        if text.startswith("/publish"):
            await self.menu_service.publish_today(binding.tenant_id, timezone_name)
            await self.client.send_message(chat_id, "📋 Menu updated ✅")
            return

        if text.startswith("/status"):
            menu = await self.menu_service.get_status(binding.tenant_id, timezone_name)
            if not menu:
                await self.client.send_message(chat_id, "No menu published yet.")
                return
            await self.client.send_message(
                chat_id,
                f"Current menu: {menu.title}. Last update: {menu.updated_at.isoformat()}",
            )
            return

        if text.startswith("/"):
            await self.client.send_message(chat_id, "Unknown command.")
            return

        await self.menu_service.update_menu_text(
            binding.tenant_id, text, "Menu of the day", timezone_name
        )
        await self.client.send_message(chat_id, "📋 Menu updated ✅")

    async def _handle_photo(self, message: TelegramMessage, binding) -> None:
        chat_id = message.chat.id
        photos = message.photo or []
        if not photos:
            return

        best = max(photos, key=lambda photo: photo.file_size or 0)
        file_info = await self.client.get_file(best.file_id)
        data = await self.client.download_file(file_info.file_path)

        if len(data) > self.max_image_bytes:
            await self.client.send_message(chat_id, "Image too large.")
            return

        tenant = await self.tenant_service.get_tenant_by_id(binding.tenant_id)
        if not tenant:
            await self.client.send_message(chat_id, "Tenant not found.")
            return

        uploads_dir = Path(self.settings.TELEGRAM_UPLOADS_DIR) / tenant.short_code
        uploads_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{message.message_id}_{best.file_unique_id}.jpg"
        file_path = uploads_dir / filename
        file_path.write_bytes(data)

        url = f"/uploads/{tenant.short_code}/{filename}"
        await self.menu_service.update_featured_image(binding.tenant_id, url, message.caption)
        await self.client.send_message(chat_id, "🖼 Image received and will be displayed ✅")

    async def poll_updates(self) -> None:
        offset = 0
        while not self._stop_event.is_set():
            updates = await self.client.get_updates(offset, 10, list(self.allowed_updates))
            for raw in updates:
                update = TelegramUpdate.model_validate(raw)
                await self.handle_update(update)
                offset = update.update_id + 1

    def stop_polling(self) -> None:
        self._stop_event.set()
