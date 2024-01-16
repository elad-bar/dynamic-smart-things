from helpers.enums import SystemAttribute
from helpers.errors import CommandError
from models.capability import CapabilityEntity


class ComponentEntity:
    def __init__(self):
        self.capabilities: dict[str, CapabilityEntity] | None = None
        self.disabled_capabilities: list[str] | None = None

    def validate_command(self, capability_id: str, command: str, args: list | None = None):
        capability = self.capabilities.get(capability_id)

        if capability is None:
            raise CommandError(f"Capability is not available")

        capability.validate_command(command, args)

    def get_system_attribute(self, attribute: SystemAttribute):
        attribute_key = str(attribute)
        capability_id = f"custom.{attribute_key}"

        capability: CapabilityEntity = self.capabilities.get(capability_id)

        if capability is None:
            return []

        return capability.get_value(attribute_key)

    @staticmethod
    def load(data: dict, device_capabilities: dict):
        component = ComponentEntity()
        component.capabilities = {}

        for capability_id in data:
            capability_data = data[capability_id]
            device_capability = device_capabilities.get(capability_id)

            capability: CapabilityEntity = CapabilityEntity.load(capability_data, device_capability)

            if capability.status == "live" or capability_id.startswith("custom."):
                component.capabilities[capability_id] = capability

        component.disabled_capabilities = component.get_system_attribute(SystemAttribute.DISABLED_CAPABILITIES)

        ignored_capabilities = [
            f"custom.{SystemAttribute.__dict__[key]}"
            for key in SystemAttribute.__dict__
            if not key.startswith("__") and not callable(SystemAttribute.__dict__[key])
        ]

        ignored_capabilities.extend(component.disabled_capabilities)

        for capability_id in ignored_capabilities:
            if capability_id in component.capabilities:
                del component.capabilities[capability_id]

        return component
