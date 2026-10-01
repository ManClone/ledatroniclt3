"""Fetch status data from the LEDATRONIC LT3."""

from __future__ import annotations

import logging
import socket
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    SOCKET_TIMEOUT,
    STATE_MAP,
    STATUS_SIZE,
    STATUS_START1,
    STATUS_START2,
    UPDATE_INTERVAL_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


def fetch_status(host: str, port: int) -> dict[str, Any]:
    """Read and decode one 56-byte status payload from the controller."""
    with socket.create_connection((host, port), timeout=SOCKET_TIMEOUT) as sock:
        sock.settimeout(SOCKET_TIMEOUT)
        while True:
            byte = sock.recv(1)
            if not byte:
                raise ConnectionError("Controller closed the connection before a frame")

            if byte != STATUS_START1:
                continue

            byte = sock.recv(1)
            if not byte:
                raise ConnectionError("Controller closed the connection before a frame")
            if byte != STATUS_START2:
                continue

            payload = bytearray()
            while len(payload) < STATUS_SIZE:
                chunk = sock.recv(STATUS_SIZE - len(payload))
                if not chunk:
                    raise ConnectionError("Controller returned an incomplete status frame")
                payload.extend(chunk)
            return parse_status(payload)


def parse_status(data: bytearray) -> dict[str, Any]:
    """Decode the controller payload using the offsets used by this integration."""
    if len(data) < STATUS_SIZE:
        raise ValueError(f"Status payload is too short: {len(data)} bytes")

    state_code = data[4]
    fan_code = data[50]
    return {
        "current_temp": data[1] + data[55] * 256,
        "current_valve_pos_target": data[2],
        "current_valve_pos_actual": data[3],
        "state_code": state_code,
        "current_state": STATE_MAP.get(
            state_code, f"Unbekannter Status: {state_code}"
        ),
        "max_temp": data[9] + data[8] * 256,
        "grundglut": data[11],
        "trend": data[12],
        "abbrande": data[26] + data[25] * 256,
        "heizfehler": data[28] + data[27] * 256,
        "puffer_unten": data[34],
        "puffer_oben": data[36],
        "vorlauf_temp": data[37],
        "schorn_temp": data[47] + data[46] * 256,
        "ventilator": {0: "off", 1: "on"}.get(fan_code, "unknown"),
    }


class LedatronicCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Share one poll of the controller between all sensor entities."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )
        self.host = entry.data["host"]
        self.port = entry.data["port"]

    async def _async_update_data(self) -> dict[str, Any]:
        """Poll the controller without blocking Home Assistant's event loop."""
        try:
            return await self.hass.async_add_executor_job(
                fetch_status, self.host, self.port
            )
        except (OSError, TimeoutError, ValueError) as err:
            raise UpdateFailed(f"Could not read LEDATRONIC LT3: {err}") from err
