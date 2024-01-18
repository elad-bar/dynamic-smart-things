import json
import logging

from aiohttp import ClientSession

from api.base_api import BaseAPI
from helpers.consts import SUCCESS_UPDATE_STATUS
from helpers.enums import Endpoint

_LOGGER = logging.getLogger(__name__)


class DevicesAPI(BaseAPI):
    def __init__(self, token: str, session: ClientSession | None):
        super().__init__(token, session)

        self._devices: list | None = None

    @property
    def endpoint(self) -> Endpoint | None:
        return Endpoint.DEVICES

    @property
    def devices(self) -> list | None:
        return self._devices

    async def _load(self) -> list | dict:
        devices = await self._get_metadata()

        for device in devices:
            device_details = await self._get_device_status(device)

            device.update(device_details)

        self._devices = devices

        return self._devices

    async def _get_device_status(self, device_data):
        params = ["deviceId"]
        params_data = {
            key: device_data[key] for key in params
        }

        params_data["status"] = "status"

        device_status = await self._get_data(params_data)

        return device_status

    def get_device_capabilities(self) -> list[str]:
        device_capabilities: list[str] = []

        for device in self._devices:
            components = device.get("components", {})

            for component_id in components:
                component = components.get(component_id)
                capabilities = list(component.keys())

                for capability_id in capabilities:
                    if capability_id not in device_capabilities:
                        device_capabilities.append(capability_id)

        return device_capabilities

    async def send_command(self,
                           device_id: str,
                           component_id: str,
                           capability_id: str,
                           command: str,
                           args=None) -> bool:

        command_data = {
            "component": component_id,
            "capability": capability_id,
            "command": command,
        }

        if args:
            command_data["args"] = args

        data = {
            "commands": [command_data]
        }

        params = {
            "deviceId": device_id
        }

        response = await self._post_data(params, data)
        if response is None:
            return False

        results = response.get("results", [])

        if len(results) == 0:
            _LOGGER.warning(
                f"Failed to execute command due to invalid response, "
                f"Request: {json.dumps(command_data)}, "
                f"Response: {results}"
            )

            return False

        result = results[0]
        result_status = result.get("status")
        is_success = result_status in SUCCESS_UPDATE_STATUS

        if not is_success:
            _LOGGER.warning(
                f"Failed to execute command, "
                f"Request: {json.dumps(command_data)}, "
                f"Response: {result}"
            )

        return is_success
