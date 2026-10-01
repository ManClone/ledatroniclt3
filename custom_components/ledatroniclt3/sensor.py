"""Sensor entities for the LEDATRONIC LT3 integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    PERCENTAGE,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import (
    AddConfigEntryEntitiesCallback,
    AddEntitiesCallback,
)
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_PORT, DOMAIN
from .coordinator import LedatronicCoordinator

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    }
)

SENSORS = (
    ("current_temp", "Brennraumtemperatur", TEMP_CELSIUS, "ledatronic_temp", "mdi:thermometer"),
    ("current_state", "Betriebszustand", None, "ledatronic_state", "mdi:fireplace"),
    ("current_valve_pos_target", "Luftklappe Sollposition", PERCENTAGE, "ledatronic_valve", "mdi:valve"),
    ("max_temp", "Maximaltemperatur", TEMP_CELSIUS, "ledatronic_maxtemp", "mdi:thermometer-alert"),
    ("grundglut", "Grundgluttemperatur", TEMP_CELSIUS, "ledatronic_grundglut", "mdi:fire"),
    ("trend", "Temperaturtrend Rohwert", None, "ledatronic_trend", "mdi:chart-line"),
    ("abbrande", "Abbrände gesamt", None, "ledatronic_abbrande", "mdi:counter"),
    ("heizfehler", "Heizfehler Zähler", None, "ledatronic_heizfehler", "mdi:alert-circle-outline"),
    ("puffer_unten", "Puffertemperatur unten", TEMP_CELSIUS, "ledatronic_puffer_unten", "mdi:thermometer"),
    ("puffer_oben", "Puffertemperatur oben", TEMP_CELSIUS, "ledatronic_puffer_oben", "mdi:thermometer"),
    ("vorlauf_temp", "Kamin Vorlauftemperatur", TEMP_CELSIUS, "ledatronic_vorlauf_temp", "mdi:heat-wave"),
    ("schorn_temp", "Schornsteintemperatur", TEMP_CELSIUS, "ledatronic_schorn_temp", "mdi:chimney"),
    ("ventilator", "Ventilator", None, "ledatronic_ventilator", "mdi:fan"),
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Import legacy YAML configuration into a UI config entry."""
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "import"},
            data={
                CONF_HOST: config[CONF_HOST],
                CONF_PORT: config.get(CONF_PORT, DEFAULT_PORT),
            },
        )
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    coordinator: LedatronicCoordinator = entry.runtime_data
    async_add_entities(
        LedatronicSensor(coordinator, entry, *description)
        for description in SENSORS
    )


class LedatronicSensor(CoordinatorEntity[LedatronicCoordinator], SensorEntity):
    """One LEDATRONIC measurement."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LedatronicCoordinator,
        entry: ConfigEntry,
        data_key: str,
        name: str,
        unit: str | None,
        object_id: str,
        icon: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.data_key = data_key
        self._attr_name = name
        self._attr_unique_id = f"{entry.unique_id}_{object_id}"
        self._attr_suggested_object_id = object_id
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
            name="LEDATRONIC LT3",
            manufacturer="LEDA",
            model="LT3",
            configuration_url=f"http://{coordinator.host}",
        )

    @property
    def native_value(self) -> Any:
        """Return the latest value shared by the coordinator."""
        return self.coordinator.data.get(self.data_key)
