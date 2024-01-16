from enum import StrEnum


class Endpoint(StrEnum):
    CAPABILITIES = "capabilities"
    DEVICES = "devices"
    LOCATIONS = "locations"


class SystemAttribute:
    DISABLED_COMPONENTS = "disabledComponents"
    DISABLED_CAPABILITIES = "disabledCapabilities"
