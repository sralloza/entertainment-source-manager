from datetime import date

from pydantic import BaseModel

from app.models.source import Source


class EpisodeBase(BaseModel):
    source_name: str
    chapter_id: str
    source: Source


class NonScheduledEpisode(EpisodeBase):
    chapter_url: str


class S3NonScheduledEpisode(BaseModel):
    source_name: str
    chapter_id: str


class ScheduledEpisode(EpisodeBase):
    released_date: date | None
    platform: str
