"""Version: 1.0.0 | Datum: 2025-12-19
Buttons for Linux Updates.
"""
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the buttons."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        LinuxUpdateRunButton(coordinator),
        LinuxRebootButton(coordinator)
    ])

class LinuxUpdateRunButton(CoordinatorEntity, ButtonEntity):
    """Button to trigger update."""

    _attr_name = "Run Updates"
    _attr_icon = "mdi:update"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_run_updates"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.trigger_update()

class LinuxRebootButton(CoordinatorEntity, ButtonEntity):
    """Button to trigger reboot."""

    _attr_name = "Reboot Server"
    _attr_icon = "mdi:restart"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_reboot_server"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.trigger_reboot()