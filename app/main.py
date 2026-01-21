from contextlib import asynccontextmanager
from pathlib import Path
import asyncio

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.settings import Settings
from app.routes.display_routes import router as display_router
from app.routes.tenant_api_routes import router as tenant_router
from app.routes.telegram_routes import router as telegram_router
from infrastructure.clients.http_client import HttpClient
from infrastructure.clients.openweather_client import OpenWeatherClient
from infrastructure.clients.telegram_client import TelegramClient
from infrastructure.persistence.mongo import MongoManager
from infrastructure.repositories.menu_repository_mongo import MenuRepositoryMongo
from infrastructure.repositories.telegram_binding_repository_mongo import TelegramBindingRepositoryMongo
from infrastructure.repositories.tenant_repository_mongo import TenantRepositoryMongo
from services.menu_service import MenuService
from services.telegram_service import TelegramService
from services.tenant_service import TenantService
from services.weather_service import WeatherService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    Path(settings.TELEGRAM_UPLOADS_DIR).mkdir(parents=True, exist_ok=True)

    mongo = MongoManager(settings.MONGO_URI, settings.MONGO_DB_NAME)
    await mongo.init_indexes()

    app.state.db = mongo.db
    app.state.mongo_client = mongo.client
    app.state.settings = settings
    app.state.http_client = HttpClient(
        base_url=settings.EMT_BASE_URL,
        timeout_seconds=settings.EMT_TIMEOUT_SECONDS,
    )
    app.state.openweather_http_client = HttpClient(
        base_url=settings.OPENWEATHER_BASE_URL,
        timeout_seconds=settings.WEATHER_TIMEOUT_SECONDS,
    )
    app.state.openweather_client = OpenWeatherClient(app.state.openweather_http_client, settings)
    app.state.weather_service = WeatherService(app.state.openweather_client, settings)
    if settings.TELEGRAM_BOT_TOKEN:
        app.state.telegram_client = TelegramClient(settings.TELEGRAM_BOT_TOKEN)
    else:
        app.state.telegram_client = None

    app.state.telegram_service = None
    app.state.telegram_polling_task = None

    if settings.TELEGRAM_MODE == "polling" and app.state.telegram_client:
        tenant_repo = TenantRepositoryMongo(app.state.db)
        menu_repo = MenuRepositoryMongo(app.state.db)
        binding_repo = TelegramBindingRepositoryMongo(app.state.db)
        tenant_service = TenantService(tenant_repo, settings)
        menu_service = MenuService(menu_repo, tenant_repo)
        app.state.telegram_service = TelegramService(
            app.state.telegram_client,
            tenant_service,
            menu_service,
            binding_repo,
            settings,
        )
        app.state.telegram_polling_task = asyncio.create_task(
            app.state.telegram_service.poll_updates()
        )

    yield

    if app.state.telegram_service:
        app.state.telegram_service.stop_polling()
        await app.state.telegram_polling_task

    await app.state.http_client.close()
    await app.state.openweather_http_client.close()
    if app.state.telegram_client:
        await app.state.telegram_client.close()
    app.state.mongo_client.close()


def create_app() -> FastAPI:
    settings = Settings()
    Path(settings.TELEGRAM_UPLOADS_DIR).mkdir(parents=True, exist_ok=True)

    app = FastAPI(lifespan=lifespan)
    app.include_router(display_router)
    app.include_router(tenant_router)
    app.include_router(telegram_router)

    app.mount("/static", StaticFiles(directory="web"), name="static")
    app.mount("/uploads", StaticFiles(directory=settings.TELEGRAM_UPLOADS_DIR), name="uploads")
    return app


app = create_app()
