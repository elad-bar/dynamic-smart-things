import logging

from helpers.consts import CAPABILITIES_MAPPING_WITH_DEPENDENCY, CAPABILITIES_MAPPING
from models.capability import CapabilityEntity
from models.device import DeviceEntity
from models.entity import Entity

_LOGGER = logging.getLogger(__name__)


class EntityManager:
    def __init__(self):
        _LOGGER.info("Initializing manager")

        self._entities: list[Entity] | None = None

        self._handlers = [
            self._default_handler,
            self._mapping_with_dependency_handler,
            self._mapping_handler,
            self._power_consumption_report_handler
        ]

        self._entity_checks = {
            "binary_sensor": self._is_binary_sensor,
            "sensor": self._is_sensor,
            "number": self._is_number,
            "select": self._is_select,
            "switch": self._is_switch,
            "ignored": self._is_ignored,
        }

    @property
    def entities(self):
        return self._entities

    def get_entities(self, entity_type: str):
        _LOGGER.info(f"Get entities for type: {entity_type}")

        entities = [
            entity
            for entity in self._entities
            if entity.type == entity_type
        ]

        return entities

    def load(self, devices: list[DeviceEntity]):
        _LOGGER.info("Loading Entity recommendation")

        self._entities = []

        for handler in self._handlers:
            for device in devices:
                for component_id in device.components:
                    component = device.components.get(component_id)

                    handler(device, component_id, component.capabilities)

    def _power_consumption_report_handler(
            self,
            device: DeviceEntity,
            component_id: str,
            component_capabilities: dict[str, CapabilityEntity]
    ):
        _LOGGER.debug(
            f"Creating power consumption report entities of {device.label}, "
            f"Component: {component_id}"
        )

        capability_id = "powerConsumptionReport"
        attribute_key = "powerConsumption"

        capability = component_capabilities.get(capability_id)

        if capability is None:
            return

        component_attributes = capability.attributes
        power_consumption_attribute = component_attributes.get(attribute_key)

        if power_consumption_attribute is not None:
            attribute_value = power_consumption_attribute.value
            if attribute_value is None:
                return

            props = power_consumption_attribute.properties.get("properties", {})

            params = [
                device.device_id,
                component_id,
                capability_id,
                attribute_key
            ]

            unique_id = ".".join(params)

            power_consumption_report_entities = [
                Entity.load(
                    device.label,
                    device.device_id,
                    component_id,
                    capability_id,
                    attribute_key,
                    "sensor",
                    props.get(attribute_sub_key),

                )
                for attribute_sub_key in attribute_value
            ]

            self._entities = [
                entity
                for entity in self._entities
                if entity.unique_id != unique_id
            ]

            self._entities.extend(power_consumption_report_entities)

    def _mapping_with_dependency_handler(
            self,
            device: DeviceEntity,
            component_id: str,
            component_capabilities: dict[str, CapabilityEntity]
    ):
        _LOGGER.debug(
            f"Creating mapped entities (with dependency) of {device.label}, "
            f"Component: {component_id}"
        )

        for entity_type in CAPABILITIES_MAPPING_WITH_DEPENDENCY:
            mappings = CAPABILITIES_MAPPING_WITH_DEPENDENCY[entity_type]

            for main_capability_id in mappings:
                if main_capability_id in component_capabilities:
                    mapped_capabilities = mappings[main_capability_id]

                    relevant_capabilities = {
                        capability_id: component_capabilities[capability_id]
                        for capability_id in component_capabilities
                        if capability_id in mapped_capabilities or capability_id == main_capability_id
                    }

                    if len(relevant_capabilities.keys()) == 1:
                        continue

                    entity = Entity.load(
                        device.label,
                        device.device_id,
                        component_id,
                        main_capability_id,
                        main_capability_id,
                        entity_type,
                        relevant_capabilities,
                    )

                    self._entities.append(entity)

    def _mapping_handler(
            self,
            device: DeviceEntity,
            component_id: str,
            component_capabilities: dict[str, CapabilityEntity]
    ):
        _LOGGER.debug(
            f"Creating mapped entities (without dependency) of {device.label}, "
            f"Component: {component_id}"
        )

        for entity_type in CAPABILITIES_MAPPING:
            mappings = CAPABILITIES_MAPPING[entity_type]

            relevant_capabilities = {
                capability_id: component_capabilities[capability_id]
                for capability_id in component_capabilities
                if capability_id in mappings
            }

            if len(relevant_capabilities.keys()) == 0:
                continue

            entity = Entity.load(
                device.label,
                device.device_id,
                component_id,
                list(relevant_capabilities.keys())[0],
                list(relevant_capabilities.keys())[0],
                entity_type,
                relevant_capabilities,
            )

            self._entities.append(entity)

    def _default_handler(
            self,
            device: DeviceEntity,
            component_id: str,
            component_capabilities: dict[str, CapabilityEntity]
    ):
        _LOGGER.debug(
            f"Creating default entities of {device.label}, "
            f"Component: {component_id}"
        )

        for capability_id in component_capabilities:
            capability = component_capabilities.get(capability_id)

            for attribute_key in capability.attributes:
                attribute = capability.attributes.get(attribute_key)

                options_number = 0
                has_min_max = False

                has_setter = attribute.default_command is not None
                property_type = None

                if attribute.properties:
                    property_type = attribute.properties.get("type")
                    options_number = len(attribute.properties.get("enum", []))
                    has_min_max = (
                        ("min" in attribute.properties or "minimum" in attribute.properties)
                        and
                        ("max" in attribute.properties or "maximum" in attribute.properties)
                    )

                entity_type = self.get_entity_type(property_type, has_setter, has_min_max, options_number)

                if entity_type is not None:
                    entity = Entity.load(
                        device.label,
                        device.device_id,
                        component_id,
                        capability_id,
                        attribute_key,
                        entity_type,
                        attribute.__dict__,
                    )

                    self._entities.append(entity)

    def get_entity_type(self, has_properties, has_setter, has_min_max, options_number):
        for entity_type in self._entity_checks:
            check = self._entity_checks.get(entity_type)
            is_match = check(has_properties, has_setter, has_min_max, options_number)

            if is_match:
                return entity_type

        return None

    @staticmethod
    def _is_ignored(property_type, _has_setter, _has_min_max, _options_number) -> bool:
        return property_type is not None

    @staticmethod
    def _is_number(property_type, has_setter, has_min_max, _options_number) -> bool:
        return (has_setter and has_min_max) or property_type in ["number", "integer"]

    @staticmethod
    def _is_switch(_property_type, has_setter, _has_min_max, options_number) -> bool:
        return has_setter and options_number == 2

    @staticmethod
    def _is_select(_property_type, has_setter, _has_min_max, options_number) -> bool:
        return has_setter and options_number > 2

    @staticmethod
    def _is_binary_sensor(_property_type, has_setter, _has_min_max, options_number) -> bool:
        return not has_setter and options_number == 2

    @staticmethod
    def _is_sensor(property_type, has_setter, _has_min_max, options_number) -> bool:
        return not has_setter and (options_number not in [0, 2] or property_type in ["number", "integer", "string"])
