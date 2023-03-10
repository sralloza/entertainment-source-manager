from app.core.common import BaseRepository
from app.settings import settings


class TelegramRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(api_base_url="https://api.telegram.org")
        pass

    async def send_message(self, message: str) -> None:
        params = {
            "chat_id": settings.telegram_chat_id,
            "text": message,
            "parse_mode": "MarkdownV2",
            "disable_web_page_preview": "true",
        }

        path = f"/bot{settings.telegram_token}/sendMessage"
        await self._send_request("GET", path, params=params)
