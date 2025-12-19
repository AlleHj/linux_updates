"""Version: 1.0.0 | Datum: 2025-12-19
DataUpdateCoordinator for Linux Updates.
"""
import asyncio
import logging
from datetime import timedelta, datetime
import asyncssh

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CMD_CHECK_UPDATES,
    CMD_LIST_PACKAGES,
    CMD_UPGRADE,
    CMD_REBOOT,
)

_LOGGER = logging.getLogger(__name__)

class LinuxUpdatesCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Linux server via SSH."""

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=6), # Check every 6 hours automatically
        )
        self.config = config
        self.host = config.get("host")
        self.port = config.get("port", 22)
        self.username = config.get("username")
        self.password = config.get("password")
        self.ssh_key = config.get("ssh_key_file")

        # State storage
        self.update_count = 0
        self.packages = []
        self.last_check_success = None
        self.last_update_success = None
        self.command_running = False
        self.error_state = False
        self.error_message = ""

    async def _async_update_data(self):
        """Fetch data from API endpoint.
        This is the automatic polling function.
        """
        if self.command_running:
            return {
                "count": self.update_count,
                "packages": self.packages,
            }

        try:
            async with self._get_connection() as conn:
                # 1. Check count (simulate upgrade)
                result_check = await conn.run(CMD_CHECK_UPDATES)
                if result_check.exit_status != 0:
                    raise UpdateFailed(f"APT check failed: {result_check.stderr}")

                # Parse 'X upgraded' from output
                output = result_check.stdout
                count = 0
                for line in output.splitlines():
                    if "upgraded," in line and "newly installed," in line:
                        parts = line.split()
                        if parts[0].isdigit():
                            count = int(parts[0])
                            break

                self.update_count = count

                # 2. Get Package List if updates exist
                package_list = []
                if count > 0:
                    result_list = await conn.run(CMD_LIST_PACKAGES)
                    # Skip the first line usually "Listing..."
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
            _LOGGER.error("SSH Connection error: %s", err)
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
            known_hosts=None, # Warning: Skips host key verification for simplicity. Prod: Use known_hosts.
        )

    async def trigger_update(self):
        """Triggers the apt-get upgrade command."""
        if self.command_running:
            _LOGGER.warning("Command already running")
            return

        self.command_running = True
        _LOGGER.info("Starting system update on %s", self.host)

        try:
            async with self._get_connection() as conn:
                # We expect this to take time, so we increase timeout or handle async
                # Using 'run' waits for completion.
                result = await conn.run(CMD_UPGRADE, check=True)

                _LOGGER.info("Update completed: %s", result.stdout)
                self.last_update_success = dt_util.now()
                self.error_state = False

                # Refresh data immediately
                await self.async_request_refresh()

        except Exception as e:
            _LOGGER.error("Update failed: %s", e)
            self.error_state = True
            self.error_message = f"Update failed: {str(e)}"
        finally:
            self.command_running = False

    async def trigger_reboot(self):
        """Triggers the reboot command."""
        try:
            async with self._get_connection() as conn:
                await conn.run(CMD_REBOOT)
                _LOGGER.info("Reboot command sent")
        except Exception as e:
             # Connection will likely drop immediately, which is expected
            _LOGGER.info("Reboot triggered (connection dropped as expected): %s", e)