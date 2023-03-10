from pydantic import BaseModel


class Settings(BaseModel):
    telegram_token: str | None = None
    telegram_chat_id: str | None = None
    todoist_api_key: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_bucket_name: str
    aws_region_name: str
    log_level: str = "DEBUG"

    @property
    def telegram_enabled(self) -> bool:
        arr = (self.telegram_token, self.telegram_chat_id)
        return None not in arr

    @property
    def valid_telegram_config(self) -> bool:
        arr = (self.telegram_token, self.telegram_chat_id)
        return arr.count(None) != 1
