import httpx
from pydantic import BaseModel


class TelegramFileInfo(BaseModel):
    file_path: str


class TelegramClient:
    def __init__(self, token: str):
        self._token = token
        self._base_url = f"https://api.telegram.org/bot{token}/"
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=20)

    async def send_message(self, chat_id: int, text: str) -> None:
        response = await self._client.post("sendMessage", json={"chat_id": chat_id, "text": text})
        response.raise_for_status()

    async def get_file(self, file_id: str) -> TelegramFileInfo:
        response = await self._client.post("getFile", json={"file_id": file_id})
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError("Telegram getFile failed")
        return TelegramFileInfo(file_path=data["result"]["file_path"])

    async def download_file(self, file_path: str) -> bytes:
        url = f"https://api.telegram.org/file/bot{self._token}/{file_path}"
        response = await self._client.get(url)
        response.raise_for_status()
        return response.content

    async def get_updates(self, offset: int, timeout: int, allowed_updates: list[str]) -> list[dict]:
        payload = {"offset": offset, "timeout": timeout, "allowed_updates": allowed_updates}
        response = await self._client.post("getUpdates", json=payload)
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError("Telegram getUpdates failed")
        return data.get("result", [])

    async def close(self) -> None:
        await self._client.aclose()
