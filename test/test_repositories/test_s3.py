from asyncio import Future
from unittest import mock

import pytest

from app.models.episodes import S3NonScheduledEpisode
from app.repositories.s3 import S3Repository


class TestS3Repository:
    @pytest.fixture(autouse=True)
    def mocks(self):
        self.session_sm = mock.patch("app.repositories.s3.aioboto3.Session")
        self.settings_sm = mock.patch("app.repositories.s3.settings")

        self.session_m = self.session_sm.start()
        self.settings_m = self.settings_sm.start()
        self.settings_m.aws_access_key_id = "aws_access_key_id"
        self.settings_m.aws_secret_access_key = "aws_secret_access_key"
        self.settings_m.aws_region_name = "aws_region_name"
        self.settings_m.aws_bucket_name = "aws_bucket_name"

        yield

        self.session_sm.stop()
        self.settings_sm.stop()

    @pytest.mark.asyncio
    @mock.patch("app.repositories.s3.S3Repository._download_s3_object")
    async def test_get_episodes(self, download_obj_m):
        download_obj_m.return_value = '["0", "1", "2", "3"]'

        result = await S3Repository().get_episodes("whatever")
        expected = [
            S3NonScheduledEpisode(source_name="whatever", chapter_id="0"),
            S3NonScheduledEpisode(source_name="whatever", chapter_id="1"),
            S3NonScheduledEpisode(source_name="whatever", chapter_id="2"),
            S3NonScheduledEpisode(source_name="whatever", chapter_id="3"),
        ]
        assert result == expected

    @pytest.mark.asyncio
    async def test_update_episodes(self):
        session_instance = self.session_m.return_value
        s3 = session_instance.client.return_value.__aenter__.return_value

        await S3Repository().update_episodes("whatever", ["0", "1", "2", "3"])
        self.session_m.assert_called_once_with(
            aws_access_key_id="aws_access_key_id",
            aws_secret_access_key="aws_secret_access_key",
            region_name="aws_region_name",
        )
        session_instance.client.assert_called_once_with("s3")
        s3.put_object.assert_called_once_with(
            Bucket="aws_bucket_name", Key="whatever", Body='["0", "1", "2", "3"]'
        )

    @pytest.mark.asyncio
    async def test_download_s3_object(self):
        session_instance = self.session_m.return_value

        s3_result: Future[bytes] = Future()
        s3_result.set_result(b"whatever")

        s3 = session_instance.client.return_value.__aenter__.return_value

        response_mock = mock.MagicMock()
        response_mock.read.return_value = s3_result
        s3.get_object.return_value = {"Body": response_mock}

        res = await S3Repository()._download_s3_object("whatever")
        assert res == "whatever"
        self.session_m.assert_called_once_with(
            aws_access_key_id="aws_access_key_id",
            aws_secret_access_key="aws_secret_access_key",
            region_name="aws_region_name",
        )
        session_instance.client.assert_called_once_with("s3")
        s3.get_object.assert_called_once_with(Bucket="aws_bucket_name", Key="whatever")
        response_mock.read.assert_called_once_with()
