"""Version: 1.5.0 | Datum: 2025-12-19
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

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_has_entity_name = True

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_update_problem"
        self._attr_name = "Update Problem" # Rent namn

    @property
    def device_info(self):
        return self.coordinator.device_info

    @property
    def is_on(self):
        return self.coordinator.error_state

    @property
    def extra_state_attributes(self):
        return {
            "error_message": self.coordinator.error_message
        }