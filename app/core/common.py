import logging
from copy import deepcopy
from datetime import date
from typing import Any

from bs4 import BeautifulSoup
from click import ClickException
from httpx import AsyncClient, Response

from app.utils.misc import get_version

_DCT = dict[str, Any] | None
logger = logging.getLogger(__name__)


class BaseRepository:
    def __init__(self, api_base_url: str, bearer_token: str | None = None):
        self.bearer_token = bearer_token
        self.api_base_url = api_base_url

    async def _send_request(
        self, method: str, path: str, data: _DCT = None, params: _DCT = None
    ) -> Response:
        headers = {
            "User-Agent": "EntertainmentSourceManager/" + get_version(),
        }
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        url = self.api_base_url + path
        async with AsyncClient(timeout=10, follow_redirects=True, headers=headers) as client:
            response = await client.request(method, url, json=data, params=params)
            if response.status_code >= 400:
                logger.error(
                    "Error sending HTTP request",
                    extra={
                        "request": {
                            "method": method,
                            "url": url,
                            "data": data,
                            "params": params,
                        },
                        "response": {
                            "status_code": response.status_code,
                            "response_body": response.text,
                            "response_headers": response.headers,
                        },
                    },
                )
                raise ClickException(
                    f"Error while fetching {url}: {response.status_code} {response.text}"
                )
            return response

    async def _send_request_soup(
        self, method: str, path: str, data: _DCT = None, params: _DCT = None
    ) -> BeautifulSoup:
        response = await self._send_request(method, path, data, params)
        return BeautifulSoup(response.text, "html.parser")

    def _normalize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        payload = deepcopy(payload)
        for key, value in payload.items():
            if isinstance(value, date):
                payload[key] = value.strftime("%Y-%m-%d")
        return payload
