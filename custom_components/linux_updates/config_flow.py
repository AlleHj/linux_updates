"""Version: 1.0.0 | Datum: 2025-12-19
Config flow for Linux Updates integration.
"""
from typing import Any
import voluptuous as vol
import asyncssh

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD, CONF_SSH_KEY

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
        vol.Optional(CONF_SSH_KEY): str,
        vol.Optional(CONF_PORT, default=22): int,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # Test connection
    try:
        client_keys = [data[CONF_SSH_KEY]] if data.get(CONF_SSH_KEY) else None
        async with asyncssh.connect(
            data[CONF_HOST],
            port=data[CONF_PORT],
            username=data[CONF_USERNAME],
            password=data.get(CONF_PASSWORD),
            client_keys=client_keys,
            known_hosts=None
        ) as conn:
            # Just check if we can run a simple echo
            await conn.run("echo test", check=True)

    except (OSError, asyncssh.Error) as err:
        raise Exception(f"Cannot connect: {err}") from err

    return {"title": f"{data[CONF_USERNAME]}@{data[CONF_HOST]}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Linux Updates."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except Exception:  # pylint: disable=broad-except
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )