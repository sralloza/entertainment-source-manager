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
    @pytest.mark.parametrize("obj", (None, '["0", "1", "2", "3"]'))
    @mock.patch("app.repositories.s3.S3Repository._download_s3_object")
    async def test_get_episodes(self, download_obj_m, obj):
        download_obj_m.return_value = obj

        result = await S3Repository().get_episodes("whatever")
        expected = [
            S3NonScheduledEpisode(source_name="whatever", chapter_id="0"),
            S3NonScheduledEpisode(source_name="whatever", chapter_id="1"),
            S3NonScheduledEpisode(source_name="whatever", chapter_id="2"),
            S3NonScheduledEpisode(source_name="whatever", chapter_id="3"),
        ]
        expected = expected if obj else []
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
    async def test_download_s3_object(self, caplog):
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

        assert len(caplog.records) == 0

    @pytest.mark.asyncio
    async def test_download_s3_object_404(self, caplog):
        exc = Exception("whatever")
        response = {"Error": {"Code": "NoSuchKey", "Message": "The specified key does not exist."}}
        setattr(exc, "response", response)
        session_instance = self.session_m.return_value

        s3 = session_instance.client.return_value.__aenter__.return_value
        s3.get_object.side_effect = exc

        res = await S3Repository()._download_s3_object("whatever")
        assert res is None
        self.session_m.assert_called_once_with(
            aws_access_key_id="aws_access_key_id",
            aws_secret_access_key="aws_secret_access_key",
            region_name="aws_region_name",
        )
        session_instance.client.assert_called_once_with("s3")
        s3.get_object.assert_called_once_with(Bucket="aws_bucket_name", Key="whatever")

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.levelname == "WARNING"
        assert record.message == "S3 object not found (bucket='aws_bucket_name', key='whatever')"

    test_data = [
        ("whatever", "The specified key does not exist."),
        ("NoSuchKey", "whatever"),
        (None, None),
    ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("code,message", test_data)
    async def test_download_s3_object_error(self, code, message, caplog):
        exc = Exception("whatever")
        if code or message:
            response = {"Error": {"Code": code, "Message": message}}
            setattr(exc, "response", response)

        session_instance = self.session_m.return_value
        s3 = session_instance.client.return_value.__aenter__.return_value
        s3.get_object.side_effect = exc

        with pytest.raises(Exception, match="whatever"):
            await S3Repository()._download_s3_object("whatever")

        self.session_m.assert_called_once_with(
            aws_access_key_id="aws_access_key_id",
            aws_secret_access_key="aws_secret_access_key",
            region_name="aws_region_name",
        )
        session_instance.client.assert_called_once_with("s3")
        s3.get_object.assert_called_once_with(Bucket="aws_bucket_name", Key="whatever")

        assert len(caplog.records) == 0
