"""Constants for the LEDATRONIC LT3 integration."""

from homeassistant.const import CONF_HOST, CONF_PORT

DOMAIN = "ledatroniclt3"
DEFAULT_PORT = 10001
SOCKET_TIMEOUT = 10
UPDATE_INTERVAL_SECONDS = 30
STATUS_START1 = b"\\x0e"
STATUS_START2 = b"\\xff"
STATUS_SIZE = 56

CONFIG_KEYS = (CONF_HOST, CONF_PORT)

STATE_MAP = {
    0: "Bereit",
    2: "Anheizen",
    3: "Heizbetrieb",
    4: "Heizbetrieb",
    7: "Grundglut",
    8: "Grundglut",
    97: "Heizfehler",
    98: "Tuer offen",
}
