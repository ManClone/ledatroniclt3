# LEDATRONIC LT3 for Home Assistant

Home Assistant custom integration for monitoring a LEDATRONIC LT3 Wi-Fi controller over the local network. It exposes stove state, chamber and flue temperatures, valve position, buffer temperatures, flow temperature, fan state, and controller counters.

## Install with HACS

1. In HACS, open **Integrations** and choose **Custom repositories** from the menu.
2. Add `https://github.com/ManClone/ledatroniclt3` with category **Integration**.
3. Download **LEDATRONIC LT3**, then restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration**, search for **LEDATRONIC LT3**, and enter the LT3 Wi-Fi module's host and TCP port. The port defaults to `10001`.

This makes the repository installable as a HACS custom repository. Inclusion in HACS's default catalog is a separate submission and review step.

## Manual installation

Copy `custom_components/ledatroniclt3` into the `custom_components` folder in your Home Assistant configuration directory, then restart Home Assistant and add the integration from **Settings → Devices & services**.

## Existing YAML installations

When the existing YAML sensor platform is detected, Home Assistant imports its host and port into a config entry. After the imported integration is working, remove the old `sensor: - platform: ledatroniclt3` section from `configuration.yaml` and restart Home Assistant.

The entity IDs are kept compatible with the legacy installation where Home Assistant can assign the previous object IDs.

## Controller compatibility

The default TCP port is `10001`. [Issue #3](https://github.com/ManClone/ledatroniclt3/issues/3) reports LEDA support's advice to use controller software V34 or newer. Another user reported V30 working with a different component version. Compatibility with older controller versions is therefore not confirmed.

The integration reads telemetry only. It does not send commands to the stove or replace the controller's safety functions.
