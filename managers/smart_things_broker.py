import json
import logging
import os
import sys

from aiohttp import ClientSession

from api.capabilities_api import CapabilitiesAPI
from api.devices_api import DevicesAPI
from api.locations_api import LocationsAPI
from helpers.consts import DIAGNOSTIC_FILE
from helpers.errors import CommandError
from managers.entity_manager import EntityManager
from models.device import DeviceEntity

_LOGGER = logging.getLogger(__name__)


class SmartThingsBroker:
    def __init__(self, token: str, session: ClientSession, device_capabilities: dict | None = None):
        self._session: ClientSession = session

        self._entity_manager = EntityManager()

        self._capabilities_api = CapabilitiesAPI(token, session, device_capabilities)
        self._devices_api = DevicesAPI(token, session)
        self._locations_api = LocationsAPI(token, session)

        self._devices: list[DeviceEntity] | None = None

    @property
    def entities(self) -> list[DeviceEntity] | None:
        return self._entity_manager.entities

    @property
    def devices(self) -> list[DeviceEntity] | None:
        return self._devices

    async def initialize(self):
        _LOGGER.info("Initializing")

        await self._capabilities_api.load()
        await self._devices_api.load()
        await self._locations_api.load()

        devices_data = self._devices_api.devices

        await self._capabilities_api.load_device_capabilities(devices_data)

        self._devices = []
        device_capabilities = self._capabilities_api.device_capabilities

        for device_data in self._devices_api.devices:
            device = DeviceEntity.load(device_data, device_capabilities)

            self._devices.append(device)

        self._entity_manager.load(self._devices)

        self.save_diagnostic_details()

    def get_entities(self, entity_type: str):
        return self._entity_manager.get_entities(entity_type)

    def _get_device(self, device_id):
        devices = [
            device
            for device in self.devices
            if device.device_id == device_id
        ]

        return None if len(devices) == 0 else devices[0]

    async def send_command(
            self,
            device_id: str,
            component_id: str,
            capability_id: str,
            command: str,
            args: list | None = None
    ) -> bool:

        result = False

        try:
            device = self._get_device(device_id)

            if device is None:
                raise CommandError(f"Device is not available")

            device.validate_command(component_id, capability_id, command, args)

            result = await self._devices_api.send_command(
                device_id,
                component_id,
                capability_id,
                command,
                args
            )

        except CommandError as ex:
            command_parts = {
                "Device": device_id,
                "Component": component_id,
                "Capability": capability_id,
                "Command": command,
            }

            error_details_parts = [
                f"{command_part}: {command_parts[command_part]}"
                for command_part in command_parts
            ]

            error_details = ", ".join(error_details_parts)

            _LOGGER.error(f"Failed to send command, Error: {ex.message}, Params: {error_details}")

        return result

    def get_diagnostic_details(self) -> dict:
        data = {
            "api": {
                "devices": self._devices_api.devices,
                "capabilities": self._capabilities_api.capabilities,
                "device_capabilities": self._capabilities_api.device_capabilities,
                "locations": self._locations_api.locations
            },
            "data": {
                "devices": self.devices,
                "entities": self.entities
            }
        }

        return data

    def save_diagnostic_details(self):
        data = self.get_diagnostic_details()

        file_path = os.path.join(sys.path[1], "data", DIAGNOSTIC_FILE)

        with open(file_path, "w+") as f:
            f.write(json.dumps(data, default=lambda o: o.__dict__, sort_keys=True, indent=4))
