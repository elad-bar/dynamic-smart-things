
class Entity:
    def __init__(self):
        self.type: str | None = None
        self.details: dict | None = None
        self.device_id: dict | None = None
        self.component_id: dict | None = None
        self.capability_id: dict | None = None
        self.attribute_id: dict | None = None

    @property
    def unique_id(self):
        return f"{self.type}::{self.device_id}.{self.component_id}.{self.capability_id}.{self.attribute_id}"

    @staticmethod
    def load(
            device_name: str,
            device_id: str,
            component_id: str,
            capability_id: str,
            attribute_id: str,
            entity_type: str,
            details: dict
    ):

        entity = Entity()

        entity.type = entity_type
        entity.details = details

        entity.device_name = device_name
        entity.device_id = device_id
        entity.component_id = component_id
        entity.capability_id = capability_id
        entity.attribute_id = attribute_id

        return entity
