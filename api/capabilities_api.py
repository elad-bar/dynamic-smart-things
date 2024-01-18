import logging

from aiohttp import ClientSession

from api.base_api import BaseAPI
from helpers.enums import Endpoint

_LOGGER = logging.getLogger(__name__)


class CapabilitiesAPI(BaseAPI):
    def __init__(self, token: str, session: ClientSession | None, device_capabilities: dict | None = None):
        super().__init__(token, session)

        self._capabilities: dict | None = None
        self._device_capabilities: dict | None = device_capabilities

    @property
    def endpoint(self) -> Endpoint | None:
        return Endpoint.CAPABILITIES

    @property
    def capabilities(self) -> dict | None:
        return self._capabilities

    @property
    def device_capabilities(self) -> dict | None:
        return self._device_capabilities

    async def _load(self) -> list | dict:
        capabilities_data = await self._get_metadata()
        capabilities = {
            capability.get("id"): capability
            for capability in capabilities_data
        }

        self._capabilities = capabilities

        return self._capabilities

    async def load_details(self, device_capabilities: list[str]):
        _LOGGER.info(f"Importing Device {self.endpoint} data")

        if self._device_capabilities is None:
            self._device_capabilities = {}

        for capability_id in device_capabilities:
            if capability_id not in self._device_capabilities:
                capability_metadata = self._capabilities.get(capability_id)

                if capability_metadata is None:
                    capability_metadata = {
                        "id": capability_id,
                        "version": 1
                    }

                device_capability = await self.get_capability(capability_metadata)

                self._device_capabilities[capability_id] = device_capability

    async def get_capability(self, capability_data):
        params = ["id", "version"]

        params_data = {
            key: str(capability_data[key])
            for key in params
        }

        capability = await self._get_data(params_data)

        return capability

    async def get_capability_presentation(self, capability_data):
        params = ["id", "version"]

        params_data = {
            key: str(capability_data[key])
            for key in params
        }

        params_data["presentation"] = "presentation"

        presentation = await self._get_data(params_data)

        return presentation
