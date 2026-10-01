"""Config flow for the LEDATRONIC LT3 integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_PORT

from .const import DEFAULT_PORT, DOMAIN
from .coordinator import fetch_status

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=65535)
        ),
    }
)


class LedatronicConfigFlow(ConfigFlow, domain=DOMAIN):
    """Set up one LEDATRONIC LT3 using its network address."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Validate the connection and create a config entry."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_PORT]
            try:
                await self.hass.async_add_executor_job(fetch_status, host, port)
            except (OSError, TimeoutError, ValueError):
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{host.lower()}:{port}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"LEDATRONIC LT3 ({host})",
                    data={CONF_HOST: host, CONF_PORT: port},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    async def async_step_import(
        self, import_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Import the existing YAML configuration."""
        host = import_data[CONF_HOST].strip()
        port = import_data.get(CONF_PORT, DEFAULT_PORT)
        await self.async_set_unique_id(f"{host.lower()}:{port}")
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=f"LEDATRONIC LT3 ({host})",
            data={CONF_HOST: host, CONF_PORT: port},
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Update the host or port for an existing entry."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_PORT]
            new_unique_id = f"{host.lower()}:{port}"
            if any(
                other.entry_id != entry.entry_id
                and other.unique_id == new_unique_id
                for other in self.hass.config_entries.async_entries(DOMAIN)
            ):
                errors["base"] = "already_configured"
            else:
                try:
                    await self.hass.async_add_executor_job(fetch_status, host, port)
                except (OSError, TimeoutError, ValueError):
                    errors["base"] = "cannot_connect"
                else:
                    return self.async_update_reload_and_abort(
                        entry,
                        data_updates={CONF_HOST: host, CONF_PORT: port},
                        unique_id=new_unique_id,
                    )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                STEP_USER_SCHEMA, entry.data
            ),
            errors=errors,
        )
