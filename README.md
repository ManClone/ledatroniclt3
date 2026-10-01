# LEDATRONIC LT3 for Home Assistant

<p align="center"><img src="custom_components/ledatroniclt3/brand/icon.png" alt="LEDATRONIC LT3 logo" width="180"></p>

Home Assistant custom integration for monitoring a LEDATRONIC LT3 Wi-Fi controller over the local network. The integration reads telemetry only. It does not send commands to the stove or replace the controller's safety functions.

## Entities and values

The integration polls the controller every 30 seconds and provides the following entities.

### Sensors

| Entity | Value | Unit / values |
| --- | --- | --- |
| Combustion chamber temperature | Current temperature reported for the combustion chamber. | °C |
| Operating state | Current operating state, decoded from the controller status code. | Text; recognized codes are listed below |
| Air valve position (target) | Requested position of the combustion-air valve. | % |
| Air valve position (actual) | Actual position of the combustion-air valve. | % |
| Maximum temperature | Maximum-temperature value reported by the controller. | °C |
| Ember bed temperature | Temperature value associated with the ember-bed phase. | °C |
| Temperature trend (raw value) | Controller trend value. It is exposed as received because its code meanings are not documented. | Raw numeric value |
| Total burns | Cumulative burn counter. | Count |
| Total heating faults | Cumulative number of heating faults. This does not identify the cause of a fault. | Count |
| Buffer tank temperature (lower) | Lower buffer-tank temperature. | °C |
| Buffer tank temperature (upper) | Upper buffer-tank temperature. | °C |
| Heating water flow temperature | Water flow temperature from the stove. | °C |
| Flue temperature | Temperature value reported for the flue/chimney. | °C |
| Fan status | Fan state reported by the controller. | `on`, `off`, or `unknown` |

The air-valve target sensor also retains the actual position as an `Istposition` state attribute for compatibility with existing dashboards.

### Binary sensors

| Entity | Turns on when |
| --- | --- |
| Heating fault active | The decoder reports status code `97` (shown as “Heizfehler” by the operating-state sensor). |
| Firebox door open | The decoder reports status code `98` (shown as “Tuer offen” by the operating-state sensor). |

These indicators represent only the two status codes currently recognized by the integration. They are not a complete alarm system and do not provide detailed alarm causes.

### Recognized operating states

| Status code | Displayed state |
| ---: | --- |
| `0` | Ready |
| `2` | Heating up |
| `3`, `4` | Heating |
| `7`, `8` | Ember bed |
| `97` | Heating fault |
| `98` | Door open |
| Any other code | Unknown status with the numeric code |

## Protocol and compatibility notes

The integration connects to the LT3 Wi-Fi module over TCP, using port `10001` by default. It reads a 56-byte status payload beginning with the `0x0E 0xFF` marker. This Wi-Fi payload layout is not publicly documented by LEDA; the field meanings above describe the integration's current decoder and are not a guarantee that every firmware version uses the same layout.

LEDA separately documents an optional Modbus TCP module and its register map. That is a different interface; its register numbers and status codes must not be assumed to match this Wi-Fi decoder. Compatibility notes for controller software versions are tracked in [issue #3](https://github.com/ManClone/ledatroniclt3/issues/3). The current Wi-Fi state-code interpretations are inherited from the existing integration and have not been independently verified against every controller firmware.

## Install with HACS

1. In HACS, open **Integrations** and choose **Custom repositories** from the menu.
2. Add `https://github.com/ManClone/ledatroniclt3` with category **Integration**.
3. Download **LEDATRONIC LT3**, then restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration**, search for **LEDATRONIC LT3**, and enter the LT3 Wi-Fi module's host and TCP port.

This makes the repository installable as a HACS custom repository. Inclusion in HACS's default catalog is a separate submission and review step.

## Manual installation

Copy `custom_components/ledatroniclt3` into the `custom_components` folder in your Home Assistant configuration directory, restart Home Assistant, and add the integration from **Settings → Devices & services**.

## Existing YAML installations

When the existing YAML sensor platform is detected, Home Assistant imports its host and port into a config entry. After the imported integration is working, remove the old `sensor: - platform: ledatroniclt3` section from `configuration.yaml` and restart Home Assistant.

Entity IDs are kept compatible with the legacy installation where Home Assistant can assign the previous object IDs.

## Controller software

[Issue #3](https://github.com/ManClone/ledatroniclt3/issues/3) reports LEDA support's advice to use controller software V34 or newer. Another user reported V30 working with a different component version, so compatibility with older controller versions is not confirmed.
