import logging
import socket
import time
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_PORT, CONF_HOST, TEMP_CELSIUS
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 10001
UPDATE_INTERVAL = 30
SOCKET_TIMEOUT = 10

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Required(CONF_HOST): cv.string,
})


STATUS_START1=b'\x0e'
STATUS_START2=b'\xff'
STATUS_END=int(56)

class LedatronicComm:
    def __init__(self, host, port):
        self.host = host;
        self.port = port;
        self.current_temp = None;
        self.max_temp = None;
        self.grundglut = None;
        self.trend = None;
        self.abbrande = None;
        self.heizfehler = None;
        self.current_state = None;
        self.current_valve_pos_target = None;
        self.current_valve_pos_actual = None;
        self.last_update = None;
        self.puffer_unten = None;
        self.puffer_oben = None;
        self.vorlauf_temp = None;
        self.schorn_temp = None;
        self.ventilator = None;

    def update(self):
        now = time.monotonic()
        if self.last_update is not None and now - self.last_update < UPDATE_INTERVAL:
            return

        # Use a bounded connection and always close it after reading one status frame.
        with socket.create_connection((self.host, self.port), timeout=SOCKET_TIMEOUT) as sock:
            sock.settimeout(SOCKET_TIMEOUT)
            while True:
                byte = sock.recv(1)
                if not byte:
                    raise ConnectionError("Connection closed before status frame")

                if byte != STATUS_START1:
                    continue

                byte = sock.recv(1)
                if not byte:
                    raise ConnectionError("Connection closed before status frame")

                if byte != STATUS_START2:
                    continue

                data = bytearray()
                while len(data) < STATUS_END:
                    chunk = sock.recv(STATUS_END - len(data))
                    if not chunk:
                        raise ConnectionError("Incomplete status frame")
                    data.extend(chunk)

                break

        self.current_temp = data[1] + (data[55] * 256)
        self.current_valve_pos_target = data[2]
        self.current_valve_pos_actual = data[3]

        state_val = data[4]
        if state_val == 0:
            self.current_state = "Bereit"
        elif state_val == 2:
            self.current_state = "Anheizen"
        elif state_val in (3, 4):
            self.current_state = "Heizbetrieb"
        elif state_val in (7, 8):
            self.current_state = "Grundglut"
        elif state_val == 97:
            self.current_state = "Heizfehler"
        elif state_val == 98:
            self.current_state = "Tuer offen"
        else:
            self.current_state = "Unbekannter Status: " + str(state_val)

        self.max_temp = data[9] + (data[8] * 256)
        self.grundglut = data[11]
        self.trend = data[12]
        self.abbrande = data[26] + (data[25] * 256)
        self.heizfehler = data[28] + (data[27] * 256)
        self.puffer_unten = data[34]
        self.puffer_oben = data[36]
        self.vorlauf_temp = data[37]
        self.schorn_temp = data[47] + (data[46] * 256)

        state_vent = data[50]
        if state_vent == 0:
            self.ventilator = "off"
        elif state_vent == 1:
            self.ventilator = "on"
        else:
            self.ventilator = "unknown"

        self.last_update = time.monotonic()

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the LEDATRONIC LT3 Wifi sensors."""
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)

    comm = LedatronicComm(host, port);

    entities = [
        LedatronicTemperatureSensor(comm),
        LedatronicStateSensor(comm),
        LedatronicValveSensor(comm),
        LedatronicMaxTemp(comm),
        LedatronicGrundglut(comm),
        LedatronicTrend(comm),
        LedatronicAbbrande(comm),
        LedatronicHeizfehler(comm),
        LedatronicPufferUnten(comm),
        LedatronicPufferOben(comm),
        LedatronicVorlaufTemp(comm),
        LedatronicSchornTemp(comm),
        LedatronicVentilator(comm),
    ]
    add_entities(entities)

class LedatronicTemperatureSensor(Entity):
    """Representation of the LedaTronic main temperatrure sensor."""

    def __init__(self, comm):
        """Initialize the sensor."""
        self.comm = comm;

    @property
    def name(self):
        """Return the name of this sensor."""
        return "ledatronic_temp"

    @property
    def state(self):
        """Return the current state of the entity."""
        return self.comm.current_temp

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return TEMP_CELSIUS

    def update(self):
        """Retrieve latest state."""
        try:
            self.comm.update();
        except (OSError, TimeoutError, ConnectionError) as err:
            _LOGGER.warning("Failed to get LEDATRONIC LT3 Wifi state: %s", err)

class LedatronicStateSensor(Entity):
    """Representation of the LedaTronic state sensor."""

    def __init__(self, comm):
        """Initialize the sensor."""
        self.comm = comm;

    @property
    def name(self):
        """Return the name of this sensor."""
        return "ledatronic_state"

    @property
    def state(self):
        """Return the current state of the entity."""
        return self.comm.current_state

    def update(self):
        """Retrieve latest state."""
        try:
            self.comm.update();
        except Exception:
            _LOGGER.error("Failed to get LEDATRONIC LT3 Wifi state.")

class LedatronicValveSensor(Entity):
    """Representation of the LedaTronic valve sensor."""

    def __init__(self, comm):
        """Initialize the sensor."""
        self.comm = comm;

    @property
    def name(self):
        """Return the name of this sensor."""
        return "ledatronic_valve"

    @property
    def state(self):
        """Return the current state of the entity."""
        return self.comm.current_valve_pos_target;

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return '%';

    def update(self):
        """Retrieve latest state."""
        try:
            self.comm.update();
        except Exception:
            _LOGGER.error("Failed to get LEDATRONIC LT3 Wifi state.")

    @property
    def device_state_attributes(self):
        """Show Device Attributes."""
        return { "Actual Position": self.comm.current_valve_pos_actual }

class LedatronicMaxTemp(Entity):
    """Representation of the LedaTronic max temperatrure."""

    def __init__(self, comm):
        """Initialize the sensor."""
        self.comm = comm;

    @property
    def name(self):
        """Return the name of this sensor."""
        return "ledatronic_maxtemp"

    @property
    def state(self):
        """Return the current state of the entity."""
        return self.comm.max_temp

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return TEMP_CELSIUS

    def update(self):
        """Retrieve latest state."""
        try:
            self.comm.update();
        except Exception:
            _LOGGER.error("Failed to get LEDATRONIC LT3 Wifi state.")

class LedatronicGrundglut(Entity):
    """Representation of the LedaTronic grundglut temperatrure."""

    def __init__(self, comm):
        """Initialize the sensor."""
        self.comm = comm;

    @property
    def name(self):
        """Return the name of this sensor."""
        return "ledatronic_grundglut"

    @property
    def state(self):
        """Return the current state of the entity."""
        return self.comm.grundglut

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return TEMP_CELSIUS

    def update(self):
        """Retrieve latest state."""
        try:
            self.comm.update();
        except Exception:
            _LOGGER.error("Failed to get LEDATRONIC LT3 Wifi state.")

class LedatronicTrend(Entity):
    """Representation of the LedaTronic trend."""

    def __init__(self, comm):
        """Initialize the sensor."""
        self.comm = comm;

    @property
    def name(self):
        """Return the name of this sensor."""
        return "ledatronic_trend"

    @property
    def state(self):
        """Return the current state of the entity."""
        return self.comm.trend;

    def update(self):
        """Retrieve latest state."""
        try:
            self.comm.update();
        except Exception:
            _LOGGER.error("Failed to get LEDATRONIC LT3 Wifi state.")

class LedatronicAbbrande(Entity):
    """Representation of the LedaTronic Abbrände."""

    def __init__(self, comm):
        """Initialize the sensor."""
        self.comm = comm;

    @property
    def name(self):
        """Return the name of this sensor."""
        return "ledatronic_abbrande"

    @property
    def state(self):
        """Return the current state of the entity."""
        return self.comm.abbrande;

    def update(self):
        """Retrieve latest state."""
        try:
            self.comm.update();
        except Exception:
            _LOGGER.error("Failed to get LEDATRONIC LT3 Wifi state.")

class LedatronicHeizfehler(Entity):
    """Representation of the LedaTronic Heizfehler."""

    def __init__(self, comm):
        """Initialize the sensor."""
        self.comm = comm;

    @property
    def name(self):
        """Return the name of this sensor."""
        return "ledatronic_heizfehler"

    @property
    def state(self):
        """Return the current state of the entity."""
        return self.comm.heizfehler;

    def update(self):
        """Retrieve latest state."""
        try:
            self.comm.update();
        except Exception:
            _LOGGER.error("Failed to get LEDATRONIC LT3 Wifi state.")

class LedatronicPufferUnten(Entity):
    """Representation of the LedaTronic valve sensor."""

    def __init__(self, comm):
        """Initialize the sensor."""
        self.comm = comm;

    @property
    def name(self):
        """Return the name of this sensor."""
        return "ledatronic_puffer_unten"

    @property
    def state(self):
        """Return the current state of the entity."""
        return self.comm.puffer_unten;

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return TEMP_CELSIUS;

    def update(self):
        """Retrieve latest state."""
        try:
            self.comm.update();
        except Exception:
            _LOGGER.error("Failed to get LEDATRONIC LT3 Wifi state.")

class LedatronicPufferOben(Entity):
    """Representation of the LedaTronic valve sensor."""

    def __init__(self, comm):
        """Initialize the sensor."""
        self.comm = comm;

    @property
    def name(self):
        """Return the name of this sensor."""
        return "ledatronic_puffer_oben"

    @property
    def state(self):
        """Return the current state of the entity."""
        return self.comm.puffer_oben;

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return TEMP_CELSIUS;

    def update(self):
        """Retrieve latest state."""
        try:
            self.comm.update();
        except Exception:
            _LOGGER.error("Failed to get LEDATRONIC LT3 Wifi state.")

class LedatronicVorlaufTemp(Entity):
    """Representation of the LedaTronic valve sensor."""

    def __init__(self, comm):
        """Initialize the sensor."""
        self.comm = comm;

    @property
    def name(self):
        """Return the name of this sensor."""
        return "ledatronic_vorlauf_temp"

    @property
    def state(self):
        """Return the current state of the entity."""
        return self.comm.vorlauf_temp;

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return TEMP_CELSIUS;

    def update(self):
        """Retrieve latest state."""
        try:
            self.comm.update();
        except Exception:
            _LOGGER.error("Failed to get LEDATRONIC LT3 Wifi state.")

class LedatronicSchornTemp(Entity):
    """Representation of the LedaTronic valve sensor."""

    def __init__(self, comm):
        """Initialize the sensor."""
        self.comm = comm;

    @property
    def name(self):
        """Return the name of this sensor."""
        return "ledatronic_schorn_temp"

    @property
    def state(self):
        """Return the current state of the entity."""
        return self.comm.schorn_temp;

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return TEMP_CELSIUS;

    def update(self):
        """Retrieve latest state."""
        try:
            self.comm.update();
        except Exception:
            _LOGGER.error("Failed to get LEDATRONIC LT3 Wifi state.")

class LedatronicVentilator(Entity):
    """Representation of the LedaTronic valve sensor."""

    def __init__(self, comm):
        """Initialize the sensor."""
        self.comm = comm;

    @property
    def name(self):
        """Return the name of this sensor."""
        return "ledatronic_ventilator"

    @property
    def state(self):
        """Return the current state of the entity."""
        return self.comm.ventilator;

    def update(self):
        """Retrieve latest state."""
        try:
            self.comm.update();
        except Exception:
            _LOGGER.error("Failed to get LEDATRONIC LT3 Wifi state.")