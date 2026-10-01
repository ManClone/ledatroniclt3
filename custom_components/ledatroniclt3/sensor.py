"""Sensor entities for the LEDATRONIC LT3 integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
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
    SensorEntityDescription(
        key="current_temp",
        translation_key="current_temp",
        suggested_object_id="ledatronic_temp",
        native_unit_of_measurement="°C",
        icon="mdi:thermometer",
    ),
    SensorEntityDescription(
        key="current_state",
        translation_key="current_state",
        suggested_object_id="ledatronic_state",
        icon="mdi:fireplace",
    ),
    SensorEntityDescription(
        key="current_valve_pos_target",
        translation_key="current_valve_pos_target",
        suggested_object_id="ledatronic_valve",
        native_unit_of_measurement="%",
        icon="mdi:valve",
    ),
    SensorEntityDescription(
        key="max_temp",
        translation_key="max_temp",
        suggested_object_id="ledatronic_maxtemp",
        native_unit_of_measurement="°C",
        icon="mdi:thermometer-alert",
    ),
    SensorEntityDescription(
        key="grundglut",
        translation_key="grundglut",
        suggested_object_id="ledatronic_grundglut",
        native_unit_of_measurement="°C",
        icon="mdi:fire",
    ),
    SensorEntityDescription(
        key="trend",
        translation_key="trend",
        suggested_object_id="ledatronic_trend",
        icon="mdi:chart-line",
    ),
    SensorEntityDescription(
        key="abbrande",
        translation_key="abbrande",
        suggested_object_id="ledatronic_abbrande",
        icon="mdi:counter",
    ),
    SensorEntityDescription(
        key="heizfehler",
        translation_key="heizfehler",
        suggested_object_id="ledatronic_heizfehler",
        icon="mdi:alert-circle-outline",
    ),
    SensorEntityDescription(
        key="puffer_unten",
        translation_key="puffer_unten",
        suggested_object_id="ledatronic_puffer_unten",
        native_unit_of_measurement="°C",
        icon="mdi:thermometer",
    ),
    SensorEntityDescription(
        key="puffer_oben",
        translation_key="puffer_oben",
        suggested_object_id="ledatronic_puffer_oben",
        native_unit_of_measurement="°C",
        icon="mdi:thermometer",
    ),
    SensorEntityDescription(
        key="vorlauf_temp",
        translation_key="vorlauf_temp",
        suggested_object_id="ledatronic_vorlauf_temp",
        native_unit_of_measurement="°C",
        icon="mdi:heat-wave",
    ),
    SensorEntityDescription(
        key="schorn_temp",
        translation_key="schorn_temp",
        suggested_object_id="ledatronic_schorn_temp",
        native_unit_of_measurement="°C",
        icon="mdi:chimney",
    ),
    SensorEntityDescription(
        key="ventilator",
        translation_key="ventilator",
        suggested_object_id="ledatronic_ventilator",
        icon="mdi:fan",
    ),
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
        LedatronicSensor(coordinator, entry, description)
        for description in SENSORS
    )


class LedatronicSensor(CoordinatorEntity[LedatronicCoordinator], SensorEntity):
    """One LEDATRONIC measurement."""

    entity_description: SensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LedatronicCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="LEDATRONIC LT3",
            manufacturer="LEDA",
            model="LT3",
        )

    @property
    def native_value(self) -> Any:
        """Return the latest value shared by the coordinator."""
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Expose the actual air-valve position alongside its target."""
        if self.entity_description.key == "current_valve_pos_target":
            return {
                "Istposition": self.coordinator.data.get(
                    "current_valve_pos_actual"
                )
            }
        return None
