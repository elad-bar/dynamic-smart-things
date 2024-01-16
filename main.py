import asyncio
import json
import logging
import os
import sys

from aiohttp import ClientSession

from helpers.consts import DIAGNOSTIC_FILE
from managers.smart_things_broker import SmartThingsBroker

DEBUG = str(os.environ.get("DEBUG", False)).lower() == str(True).lower()

log_level = logging.DEBUG if DEBUG else logging.INFO

root = logging.getLogger()
root.setLevel(log_level)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(log_level)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
stream_handler.setFormatter(formatter)
root.addHandler(stream_handler)

_LOGGER = logging.getLogger(__name__)


class MainApp:
    def __init__(self):
        self._token = os.environ.get("TOKEN")

        self._session: ClientSession | None = None
        self._broker: SmartThingsBroker | None = None

        self._file_path = os.path.join(sys.path[1], "data", DIAGNOSTIC_FILE)

    async def initialize(self):
        self._session = ClientSession()

        device_capabilities: dict | None = None

        if os.path.exists(self._file_path):
            with open(self._file_path, "r") as f:
                diagnostic_data = json.load(f)

                device_capabilities = diagnostic_data.get("api", {}).get("device_capabilities")

        self._broker = SmartThingsBroker(self._token, self._session, device_capabilities)

        await self._broker.initialize()

        self._broker.save_diagnostic_details()

    async def terminate(self):
        if self._session is not None:
            await self._session.close()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    instance = MainApp()

    try:
        loop.run_until_complete(instance.initialize())
    finally:
        loop.run_until_complete(instance.terminate())
        loop.close()
