"""Version: 1.9.0 | Datum: 2025-12-19
DataUpdateCoordinator for Linux Updates.
"""
import asyncio
import logging
from datetime import timedelta, datetime
import asyncssh

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CMD_CHECK_UPDATES,
    CMD_LIST_PACKAGES,
    CMD_UPGRADE,
    CMD_REBOOT,
    CONF_DEBUG,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL
)

_LOGGER = logging.getLogger(__name__)

class LinuxUpdatesCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Linux server via SSH."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        self.config = entry.data
        self.options = entry.options

        scan_interval_hours = self.config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=scan_interval_hours),
        )

        self.host = self.config.get("host")
        self.port = self.config.get("port", 22)
        self.username = self.config.get("username")
        self.password = self.config.get("password")
        self.ssh_key = self.config.get("ssh_key_file")

        self.debug_mode = self.config.get(CONF_DEBUG, False)

        # State storage
        self.update_count = 0
        self.packages = []
        self.last_check_success = None
        self.last_update_success = None
        self.command_running = False
        self.error_state = False
        self.error_message = ""

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info for the Device Registry."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.host)},
            name=f"Linux Server ({self.host})",
            manufacturer="Linux",
            model="SSH Managed Server",
            sw_version="Unknown",
        )

    def _log(self, level, msg, *args):
        """Internal helper to log only if debug is enabled or level is high."""
        if self.debug_mode or level >= logging.WARNING:
            _LOGGER.log(level, msg, *args)

    async def _async_update_data(self):
        """Fetch data from API endpoint. This runs 'apt-get -s upgrade'."""
        if self.command_running:
            return {
                "count": self.update_count,
                "packages": self.packages,
            }

        try:
            self._log(logging.INFO, "Checking for updates on %s...", self.host)

            async with self._get_connection() as conn:
                # 1. Check count (simulate upgrade - Safe Mode)
                result_check = await conn.run(CMD_CHECK_UPDATES)
                if result_check.exit_status != 0:
                    raise UpdateFailed(f"APT check failed: {result_check.stderr}")

                output = result_check.stdout
                self._log(logging.DEBUG, "APT Check Output: %s", output)

                count = 0
                # Parsing logic for 'apt-get -s upgrade'
                # Looks for: "26 upgraded, 0 newly installed..."
                for line in output.splitlines():
                    if "upgraded," in line and "newly installed," in line:
                        parts = line.split()
                        if parts[0].isdigit():
                            count = int(parts[0])
                            self._log(logging.DEBUG, "Parsed Safe Update Count: %s", count)
                            break

                self.update_count = count

                # 2. Get Package List
                # We fetch the list just to show what IS available, even if we don't install it all.
                package_list = []
                if count > 0:
                    result_list = await conn.run(CMD_LIST_PACKAGES)
                    lines = result_list.stdout.splitlines()
                    for line in lines:
                        if "/" in line and "upgradable" in line:
                            package_list.append(line.split("/")[0])

                self.packages = package_list
                self.last_check_success = dt_util.now()
                self.error_state = False
                self.error_message = ""

                return {
                    "count": self.update_count,
                    "packages": self.packages,
                }

        except (asyncssh.Error, OSError) as err:
            self.error_state = True
            self.error_message = str(err)
            self._log(logging.ERROR, "SSH Connection error: %s", err)
            raise UpdateFailed(f"Error communicating with server: {err}")

    def _get_connection(self):
        """Helper to establish SSH connection."""
        client_keys = [self.ssh_key] if self.ssh_key else None
        return asyncssh.connect(
            self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            client_keys=client_keys,
            known_hosts=None,
        )

    async def trigger_update(self):
        """Triggers the apt-get upgrade command."""
        if self.command_running:
            return

        self.command_running = True
        self._log(logging.INFO, "Starting system update...")

        try:
            async with self._get_connection() as conn:
                # Runs the safe upgrade command
                result = await conn.run(CMD_UPGRADE, check=True)
                self._log(logging.INFO, "Update completed. Output: %s", result.stdout)
                self.last_update_success = dt_util.now()
                self.error_state = False

                # Refresh data immediately
                await self.async_request_refresh()

        except Exception as e:
            self._log(logging.ERROR, "Update failed: %s", e)
            self.error_state = True
            self.error_message = f"Update failed: {str(e)}"
        finally:
            self.command_running = False

    async def trigger_reboot(self):
        """Triggers the reboot command."""
        self._log(logging.INFO, "Triggering reboot...")
        try:
            async with self._get_connection() as conn:
                await conn.run(CMD_REBOOT)
        except Exception as e:
            self._log(logging.INFO, "Reboot command sent (connection drop expected): %s", e)