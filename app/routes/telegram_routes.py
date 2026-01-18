import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

from app.dependencies import get_settings, get_telegram_service
from app.settings import Settings
from schemas.telegram_schemas import TelegramUpdate
from services.telegram_service import TelegramService

router = APIRouter()
logger = logging.getLogger("telegram")


@router.post("/api/telegram/webhook/{secret}")
async def telegram_webhook(
    secret: str,
    request: Request,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings),
    telegram_service: TelegramService = Depends(get_telegram_service),
) -> dict:
    if not settings.TELEGRAM_WEBHOOK_SECRET or secret != settings.TELEGRAM_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    payload = await request.json()
    update = TelegramUpdate.model_validate(payload)
    message = update.message or update.edited_message
    if message:
        logger.info(
            "telegram update_id=%s message_id=%s chat_id=%s",
            update.update_id,
            message.message_id,
            message.chat.id,
        )

    await telegram_service.handle_update(update, background_tasks)
    return {"ok": True}
