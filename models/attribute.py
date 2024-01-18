import logging
from copy import copy

from models.command import CommandEntity

_LOGGER = logging.getLogger(__name__)


class AttributeEntity:
    def __init__(self):
        self.value: str | None = None
        self.default_command: dict | None = None
        self.value: str | dict | list | float | int | None = None
        self.properties: dict | None = None

    @staticmethod
    def load(data: dict, capability_attribute: dict, commands: list[CommandEntity] | None):
        _LOGGER.debug(f"Loading attribute, Data: {data}")

        entity = AttributeEntity()

        schema = capability_attribute.get("schema", {})
        command_name = capability_attribute.get("setter")

        default_command = [
            copy(command)
            for command in commands
            if command_name is not None and command.command == command_name
        ]

        entity.value = data.get("value")
        entity.properties = schema.get("properties", {}).get("value")

        entity.default_command = None if len(default_command) == 0 else default_command[0]

        return entity
