# dynamic-smart-things

## SmartThings library POC supporting:

- Importing devices, components, capabilities and attributes
- Importing locations and rooms
- Importing capabilities and their details
- Performing commands including validation (all capabilities with commands are supported)
- Future support of additional capabilities and attributes
- Excluding components and capabilities marked as disabled
- Diagnostic details for debugging available over function (HA can use it for diagnostic of integration)
- Dynamically mapping simple entities to binary_sensor, sensor, number, switch, select
- Dynamically mapping complex entities to climate, fan, media_player, light, lock

## How to use

### Environment Variables

DEBUG - for logs with debug log level, optional, default False.
TOKEN - API Key from Samsung SmartThings developer portal, required.

### Run

```bash
python main.py
```