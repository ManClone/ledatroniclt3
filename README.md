# LEDATRONIC LT3 for Home Assistant

This custom integration reads status data from a LEDATRONIC LT3 controller over the local network and exposes it as Home Assistant sensors.

## Requirements

- The controller must be reachable from Home Assistant on the local network.
- The default TCP port is `10001`.
- Issue [#3](https://github.com/ManClone/ledatroniclt3/issues/3) reports that LEDATRONIC controller software V34 or newer is required according to LEDA support. Another user reported using V30 with a different version of this component, so compatibility with older controller software is not confirmed.

## Manual installation

1. Create `custom_components/ledatroniclt3` in your Home Assistant configuration directory.
2. Copy `__init__.py`, `manifest.json`, and `sensor.py` from this repository into that folder.
3. Add the following to `configuration.yaml`, replacing the example address with the controller's IP address:

```yaml
sensor:
  - platform: ledatroniclt3
    host: 192.168.1.100
    # Optional; defaults to 10001
    port: 10001
```

4. Restart Home Assistant.

This integration uses the YAML sensor platform setup present in this repository. The repository does not declare a tested Home Assistant version.

## Sensors

The integration exposes the controller state, temperatures, valve positions, trend, burn count, heating-error count, and fan status.

## Troubleshooting

- Confirm the controller IP address and TCP port are reachable from the Home Assistant host.
- Check the Home Assistant logs for connection or timeout errors.
- Confirm the controller software version in the LEDATRONIC app; the reported V34 requirement has not been independently verified here.
