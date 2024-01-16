API_BASE = "https://api.smartthings.com/v1/"

DIAGNOSTIC_FILE = "diagnostic.json"

SUCCESS_UPDATE_STATUS = ["ACCEPTED", "COMPLETED"]

CAPABILITIES_MAPPING_WITH_DEPENDENCY = {
    "climate": {
        "temperatureMeasurement": [
            "thermostatFanMode",
            "thermostatHeatingSetpoint",
            "thermostatCoolingSetpoint",
            "thermostatMode",
            "thermostatOperatingState",
            "thermostatSetpoint",
            "custom.thermostatSetpointControl"
        ]
    },
    "light": {
        "switch": [
            "switchLevel",
            "colorControl",
            "colorTemperature"
        ]
    }
}

CAPABILITIES_MAPPING = {
    "media_player": [
        "audioMute", "audioVolume", "mediaInputSource", "mediaPlayback", "mediaTrackControl"
    ],
    "fan": [
        "fanOscillationMode", "fanSpeed", "fanSpeedPercent"
    ],
    "lock": [
        "lock", "lockCodes", "lockOnly"
    ]
}
