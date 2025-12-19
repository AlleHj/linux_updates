"""Version: 1.0.0 | Datum: 2025-12-19
Constants for the Linux Updates integration.
"""

DOMAIN = "linux_updates"

CONF_HOST = "host"
CONF_PORT = "port"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SSH_KEY = "ssh_key_file"

DEFAULT_PORT = 22
DEFAULT_NAME = "Linux Server"

# Commands
CMD_CHECK_UPDATES = "apt-get -s -o Debug::NoLocking=true upgrade"
CMD_LIST_PACKAGES = "apt list --upgradable"
CMD_UPGRADE = "sudo DEBIAN_FRONTEND=noninteractive apt-get update && sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && sudo apt-get autoremove -y"
CMD_REBOOT = "sudo reboot"

# Attributes
ATTR_PACKAGES = "packages"
ATTR_LAST_CHECK = "last_check_success"
ATTR_LAST_UPDATE = "last_update_success"