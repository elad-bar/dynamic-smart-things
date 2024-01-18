import logging
import sys

from aiohttp import ClientSession

from helpers.consts import API_BASE
from helpers.enums import Endpoint

_LOGGER = logging.getLogger(__name__)


class BaseAPI:
    def __init__(self, token: str, session: ClientSession | None):
        self._token = token
        self._data: dict | list | None = None
        self._session: ClientSession | None = session

        self._headers = {"Authorization": "Bearer " + self._token}

    @property
    def endpoint(self) -> Endpoint | None:
        return None

    async def load(self):
        _LOGGER.info(f"Importing {self.endpoint} data")

        await self._load()

    async def _load(self) -> list | dict:
        pass

    async def _get_metadata(self):
        result = None
        url = f"{API_BASE}{self.endpoint}"

        try:
            async with self._session.request("get", url, headers=self._headers) as resp:
                resp.raise_for_status()

                data = await resp.json()
                result = data["items"]

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to get data, URL: {url}, Error: {ex}, Line: {line_number}"
            )

        return result

    async def _get_data(self, params: dict):
        endpoint_data = "/".join(params.values())

        url = f"{API_BASE}{self.endpoint}/{endpoint_data}"

        try:
            async with self._session.request("get", url, headers=self._headers) as resp:
                resp.raise_for_status()

                return await resp.json()

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to get data, URL: {url}, Error: {ex}, Line: {line_number}"
            )

    async def _post_data(self, params: dict, data: dict | list):
        endpoint_data = "/".join(params.values())

        url = f"{API_BASE}{self.endpoint}/{endpoint_data}"

        try:
            async with self._session.request("post", url, headers=self._headers, data=data) as resp:
                resp.raise_for_status()

                return await resp.json()

        except Exception as ex:
            exc_type, exc_obj, tb = sys.exc_info()
            line_number = tb.tb_lineno

            _LOGGER.error(
                f"Failed to post data, URL: {url}, Data: {data}, Error: {ex}, Line: {line_number}"
            )
