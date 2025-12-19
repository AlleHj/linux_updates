"""Version: 1.7.0 | Datum: 2025-12-19
Config flow for Linux Updates integration.
"""
from typing import Any
import voluptuous as vol
import asyncssh

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SSH_KEY,
    CONF_DEBUG,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    try:
        client_keys = [data[CONF_SSH_KEY]] if data.get(CONF_SSH_KEY) else None

        # Test connection
        async with asyncssh.connect(
            data[CONF_HOST],
            port=data[CONF_PORT],
            username=data[CONF_USERNAME],
            password=data.get(CONF_PASSWORD),
            client_keys=client_keys,
            known_hosts=None
        ) as conn:
            await conn.run("echo test", check=True)

    except (OSError, asyncssh.Error) as err:
        raise Exception(f"Cannot connect: {err}") from err

    return {"title": f"{data[CONF_USERNAME]}@{data[CONF_HOST]}"}

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Linux Updates."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except Exception:
                errors["base"] = "cannot_connect"

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_USERNAME): str,
            vol.Optional(CONF_PASSWORD): str,
            vol.Optional(CONF_SSH_KEY): str,
            vol.Optional(CONF_PORT, default=22): int,
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int, # Nytt fält
            vol.Optional(CONF_DEBUG, default=False): bool,
        })

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Linux Updates."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)

                self.hass.config_entries.async_update_entry(
                    self._config_entry,
                    data=user_input
                )

                return self.async_create_entry(title="", data=user_input)

            except Exception:
                errors["base"] = "cannot_connect"

        current_data = self._config_entry.data

        schema = vol.Schema({
            vol.Required(CONF_HOST, default=current_data.get(CONF_HOST)): str,
            vol.Required(CONF_USERNAME, default=current_data.get(CONF_USERNAME)): str,
            vol.Optional(CONF_PASSWORD, default=current_data.get(CONF_PASSWORD)): str,
            vol.Optional(CONF_SSH_KEY, default=current_data.get(CONF_SSH_KEY)): str,
            vol.Optional(CONF_PORT, default=current_data.get(CONF_PORT, 22)): int,
            vol.Optional(CONF_SCAN_INTERVAL, default=current_data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): int, # Nytt fält
            vol.Optional(CONF_DEBUG, default=current_data.get(CONF_DEBUG, False)): bool,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors
        )