import logging

from helpers.errors import CommandError
from models.attribute import AttributeEntity
from models.command import CommandEntity

_LOGGER = logging.getLogger(__name__)


class CapabilityEntity:
    def __init__(self):
        self.name: str | None = None
        self.status: str | None = None
        self.name: str | None = None
        self.attributes: dict[str, AttributeEntity] | None = None
        self.commands: list[CommandEntity] | None = None

    def validate_command(self, command: str, args: list | None = None):
        commands = [
            command_item
            for command_item in self.commands
            if command_item.command == command
        ]

        if not any(commands):
            raise CommandError(f"Command is not available")

        command_item = commands[0]

        command_item.validate_command(args)

    def get_disabled_components(self) -> list[str]:
        attribute: AttributeEntity = self.attributes.get("disabledComponents")

        if attribute is None:
            return []

        return attribute.value

    def get_value(self, attribute_key) -> list[str]:
        attribute: AttributeEntity = self.attributes.get(attribute_key)

        if attribute is None:
            return []

        return attribute.value

    @staticmethod
    def load(data: dict, device_capability: dict):
        _LOGGER.debug(f"Loading capability, Data: {data}")

        entity = CapabilityEntity()

        entity.name = device_capability.get("name")
        entity.status = device_capability.get("status")
        entity.attributes = {}

        commands = device_capability.get("commands")

        entity.commands = [
            CommandEntity.load({
                "command": command_key,
                "arguments": commands[command_key].get("arguments")
            })
            for command_key in commands
        ]

        for attribute_key in data:
            device_attribute = data.get(attribute_key)
            device_capability_attribute = device_capability.get("attributes")
            capability_attribute = device_capability_attribute.get(attribute_key)

            entity.attributes[attribute_key] = AttributeEntity.load(device_attribute,
                                                                    capability_attribute,
                                                                    entity.commands)

        return entity
