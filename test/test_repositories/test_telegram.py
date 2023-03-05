from unittest import mock

import pytest
from click import ClickException
from furl import furl
from pytest_httpx import HTTPXMock

from app.repositories.telegram import TelegramRepository


@mock.patch("app.repositories.telegram.settings")
@pytest.mark.asyncio
async def test_send_message(settings_mock, httpx_mock: HTTPXMock):
    settings_mock.telegram_token = "test"
    httpx_mock.add_response(content=b'{"ok": true}')
    await TelegramRepository().send_message("chat_id", "message")
    request = httpx_mock.get_request()

    assert request is not None
    assert request.method == "GET"
    url = furl(str(request.url))
    assert url.path == "/bottest/sendMessage"
    assert url.query.params == {
        "chat_id": "chat_id",
        "text": "message",
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": "true",
    }


@pytest.mark.asyncio
async def test_send_message_fail(httpx_mock: HTTPXMock):
    httpx_mock.add_response(content=b'{"message": "Forbidden"}', status_code=403)
    with pytest.raises(ClickException, match="Error while fetching .*: 403 .*"):
        await TelegramRepository().send_message("chat_id", "message")
