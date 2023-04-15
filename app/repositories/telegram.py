from app.core.common import BaseRepository
from app.settings import settings

SPECIAL_TG_CHARS = ".-"


class TelegramRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(api_base_url="https://api.telegram.org")
        pass

    async def send_message(self, message: str) -> None:
        if not settings.telegram_enabled:
            return
        params = {
            "chat_id": settings.telegram_chat_id,
            "text": self._normalize_for_markdown_v2(message),
            "parse_mode": "MarkdownV2",
            "disable_web_page_preview": "true",
        }

        path = f"/bot{settings.telegram_token}/sendMessage"
        await self._send_request("GET", path, params=params)

    def _normalize_for_markdown_v2(self, text: str) -> str:
        for char in SPECIAL_TG_CHARS:
            text = text.replace(char, f"\\{char}")
        return text
