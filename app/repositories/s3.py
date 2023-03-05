from json import dumps, loads

import aioboto3

from app.models.episodes import S3NonScheduledEpisode
from app.settings import settings


class S3Repository:
    async def get_episodes(self, source_name: str) -> list[S3NonScheduledEpisode]:
        obj = await self._download_s3_object(source_name)
        obj_json: list[str] = loads(obj)
        return [S3NonScheduledEpisode(source_name=source_name, chapter_id=x) for x in obj_json]

    async def update_episodes(self, source_name: str, episode_ids: list[str]) -> None:
        data = dumps(episode_ids)
        session = self._create_session()
        async with session.client("s3") as s3:
            await s3.put_object(
                Bucket=settings.aws_bucket_name,
                Key=source_name,
                Body=data,
            )

    def _create_session(self) -> aioboto3.Session:
        return aioboto3.Session(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region_name,
        )

    async def _download_s3_object(self, key: str) -> str:
        session = self._create_session()
        async with session.client("s3") as s3:
            response = await s3.get_object(Bucket=settings.aws_bucket_name, Key=key)
            data: bytes = await response["Body"].read()
        return data.decode("utf-8")
