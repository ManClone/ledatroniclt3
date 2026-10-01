"""Binary status indicators for the LEDATRONIC LT3."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LedatronicCoordinator

BINARY_SENSORS = (
    (BinarySensorEntityDescription(
        key="heating_fault",
        translation_key="heating_fault",
        device_class=BinarySensorDeviceClass.PROBLEM,
    ), 97),
    (BinarySensorEntityDescription(
        key="door_open",
        translation_key="door_open",
        device_class=BinarySensorDeviceClass.DOOR,
    ), 98),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up binary status indicators."""
    coordinator: LedatronicCoordinator = entry.runtime_data
    async_add_entities(
        LedatronicBinarySensor(coordinator, entry, description, state_code)
        for description, state_code in BINARY_SENSORS
    )


class LedatronicBinarySensor(
    CoordinatorEntity[LedatronicCoordinator], BinarySensorEntity
):
    """Represent one recognized controller status as a binary sensor."""

    entity_description: BinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LedatronicCoordinator,
        entry: ConfigEntry,
        description: BinarySensorEntityDescription,
        state_code: int,
    ) -> None:
        """Initialize the status indicator."""
        super().__init__(coordinator)
        self.entity_description = description
        self._state_code = state_code
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="LEDATRONIC LT3",
            manufacturer="LEDA",
            model="LT3",
        )

    @property
    def is_on(self) -> bool:
        """Return whether the controller reports this status."""
        return self.coordinator.data.get("state_code") == self._state_code
