from pydantic import BaseModel


class Settings(BaseModel):
    telegram_token: str
    todoist_api_key: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_bucket_name: str
    aws_region_name: str
    log_level: str = "DEBUG"
