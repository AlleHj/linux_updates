"""Version: 1.7.0 | Datum: 2025-12-19
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
        LinuxRebootButton(coordinator),
        LinuxCheckButton(coordinator) # Ny knapp
    ])

class LinuxUpdateRunButton(CoordinatorEntity, ButtonEntity):
    """Button to trigger update."""

    _attr_icon = "mdi:update"
    _attr_has_entity_name = True

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_run_updates"
        self._attr_name = "Run Updates"

    @property
    def device_info(self):
        return self.coordinator.device_info

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.trigger_update()

class LinuxRebootButton(CoordinatorEntity, ButtonEntity):
    """Button to trigger reboot."""

    _attr_icon = "mdi:restart"
    _attr_has_entity_name = True

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_reboot_server"
        self._attr_name = "Reboot Server"

    @property
    def device_info(self):
        return self.coordinator.device_info

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.trigger_reboot()

class LinuxCheckButton(CoordinatorEntity, ButtonEntity):
    """Button to manually check for updates (refresh)."""

    _attr_icon = "mdi:refresh"
    _attr_has_entity_name = True

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_check_updates"
        self._attr_name = "Check for Updates"

    @property
    def device_info(self):
        return self.coordinator.device_info

    async def async_press(self) -> None:
        """Handle the button press."""
        # This forces the coordinator to run _async_update_data immediately
        await self.coordinator.async_request_refresh()