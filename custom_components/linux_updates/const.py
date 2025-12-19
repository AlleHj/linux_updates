"""Version: 1.10.0 | Datum: 2025-12-19
Constants for the Linux Updates integration.
"""

DOMAIN = "linux_updates"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SSH_KEY = "ssh_key_file"
CONF_DEBUG = "debug_logging"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_PORT = 22
DEFAULT_NAME = "Linux Server"
DEFAULT_SCAN_INTERVAL = 6

# Commands
# VIKTIGT: Vi använder fullständiga sökvägar (/usr/bin/apt-get) för att matcha sudoers exakt.
CMD_CHECK_UPDATES = "LANG=C /usr/bin/apt-get -s -o Debug::NoLocking=true upgrade"

CMD_LIST_PACKAGES = "LANG=C /usr/bin/apt list --upgradable"

# Update command: Clean, Update, Upgrade (Safe), Autoremove
# Vi använder fullständiga sökvägar här också.
# Vi tog bort DEBIAN_FRONTEND=noninteractive och använder flaggan -y som oftast räcker för safe upgrade.
CMD_UPGRADE = "sudo /usr/bin/apt-get update && sudo /usr/bin/apt-get upgrade -y && sudo /usr/bin/apt-get autoremove -y"

# Reboot command
# Även här måste vi matcha sudoers exakt (/usr/sbin/reboot)
CMD_REBOOT = "sudo /usr/sbin/reboot"

# Attributes
ATTR_PACKAGES = "packages"
ATTR_LAST_CHECK = "last_check_success"
ATTR_LAST_UPDATE = "last_update_success"