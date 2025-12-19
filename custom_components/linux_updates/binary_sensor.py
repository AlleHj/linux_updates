"""Version: 1.0.0 | Datum: 2025-12-19
Binary sensors for Linux Updates.
"""
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
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
    """Set up the binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LinuxUpdateProblemSensor(coordinator)])

class LinuxUpdateProblemSensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of an Error State."""

    _attr_name = "Update Problem"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_update_problem"

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self.coordinator.error_state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "error_message": self.coordinator.error_message
        }