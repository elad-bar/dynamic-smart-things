import logging

from aiohttp import ClientSession

from api.base_api import BaseAPI
from helpers.enums import Endpoint

_LOGGER = logging.getLogger(__name__)


class LocationsAPI(BaseAPI):
    def __init__(self, token: str, session: ClientSession | None):
        super().__init__(token, session)

        self._locations: list | None = None

    @property
    def locations(self) -> list | None:
        return self._locations

    @property
    def endpoint(self) -> Endpoint | None:
        return Endpoint.LOCATIONS

    async def _load(self) -> list | dict:
        locations = await self._get_metadata()

        for location in locations:
            location_details = await self._get_location_details(location)
            location_rooms = await self._get_location_rooms(location)

            location_rooms_items = [room for room in location_rooms.get("items")]

            location_details["rooms"] = location_rooms_items

            location.update(location_details)

        self._locations = locations

        return self._locations

    async def _get_location_details(self, location_data):
        params = ["locationId"]
        params_data = {
            key: location_data[key] for key in params
        }

        device_status = await self._get_data(params_data)

        return device_status

    async def _get_location_rooms(self, location_data):
        params = ["locationId"]
        params_data = {
            key: location_data[key] for key in params
        }

        params_data["rooms"] = "rooms"

        location_rooms = await self._get_data(params_data)

        return location_rooms
