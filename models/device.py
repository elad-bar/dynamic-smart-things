from helpers.enums import SystemAttribute
from helpers.errors import CommandError
from models.component import ComponentEntity


class DeviceEntity:
    def __init__(self):
        self.device_id: str | None = None
        self.label: str | None = None
        self.manufacturer_name: str | None = None
        self.device_manufacturer_code: str | None = None
        self.owner_id: str | None = None
        self.room_id: str | None = None
        self.components: dict[str, ComponentEntity] | None = None
        self.disabled_components: list[str] | None = None

    def validate_command(self, component_id: str, capability_id: str, command: str, args: list | None = None):
        component = self.components.get(component_id)

        if component is None:
            raise CommandError(f"Component is not available")

        component.validate_command(capability_id, command, args)

    @staticmethod
    def load(data: dict, device_capabilities: dict):
        device = DeviceEntity()
        device.device_id = data.get("deviceId")
        device.label = data.get("label")
        device.manufacturer_name = data.get("manufacturerName")
        device.device_manufacturer_code = data.get("deviceManufacturerCode")
        device.owner_id = data.get("ownerId")
        device.room_id = data.get("roomId")
        device.components = {}

        device_components = data.get("components")

        for component_id in device_components:
            device_component = device_components.get(component_id)

            device.components[component_id] = ComponentEntity.load(device_component, device_capabilities)

        main_component: ComponentEntity = device.components.get("main")

        if main_component:
            device.disabled_components = main_component.get_system_attribute(SystemAttribute.DISABLED_COMPONENTS)

            for component_id in device.disabled_components:
                if component_id in device.disabled_components:
                    del device.components[component_id]

        return device
