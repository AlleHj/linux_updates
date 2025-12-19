"""Version: 1.0.1 | Datum: 2025-12-19
Sensors for Linux Updates.
"""
from datetime import datetime
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ATTR_PACKAGES

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        LinuxUpdatesSensor(coordinator),
        LinuxLastCheckSensor(coordinator),
        LinuxLastUpdateSensor(coordinator)
    ])

class LinuxUpdatesSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Pending Updates"
    _attr_icon = "mdi:package-variant"
    _attr_native_unit_of_measurement = "updates"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_pending_updates"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.update_count

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            ATTR_PACKAGES: self.coordinator.packages
        }

class LinuxLastCheckSensor(CoordinatorEntity, SensorEntity):
    """Timestamp for last successful check."""
    _attr_name = "Last Check Success"
    _attr_device_class = "timestamp"
    _attr_icon = "mdi:clock-check"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_last_check"

    @property
    def native_value(self):
        val = self.coordinator.last_check_success
        if isinstance(val, datetime):
            return val
        return None

class LinuxLastUpdateSensor(CoordinatorEntity, SensorEntity):
    """Timestamp for last successful upgrade."""
    _attr_name = "Last Upgrade Success"
    _attr_device_class = "timestamp"
    _attr_icon = "mdi:history"

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_last_update"

    @property
    def native_value(self):
        # Safety check: Ensure we only return a datetime object
        val = self.coordinator.last_update_success
        if isinstance(val, datetime):
            return val
        return None