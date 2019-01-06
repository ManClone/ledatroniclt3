"""
Support for getting temperature and state from LEDATronic LT3 Wifi devices.

configuration.yaml:

sensors:
    - platform: ledatroniclt3
      host: 192.168.178.222

"""
import logging
import socket
import datetime;
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_PORT, CONF_HOST, TEMP_CELSIUS
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 10001

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Required(CONF_HOST): cv.string,
})

LEDA_SENSORS = []

STATUS_START1=b'\x0e'
STATUS_START2=b'\xff'
STATUS_END1=int(13)
STATUS_END2=int(255)

class LedatronicComm:
    def __init__(self, host, port):
        self.host = host;
        self.port = port;
        self.current_temp = None;
        self.current_state = None;
        self.current_valve_pos_target = None;
        self.current_valve_pos_actual = None;
        self.last_update = None;

    def update(self):
        # update at most every 10 seconds
        if self.last_update != None and (datetime.datetime.now() - self.last_update) < datetime.timedelta(seconds=10):
            return;

        self.last_update = datetime.datetime.now();

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port));

        while True:
            byte = s.recv(1)
            if byte == b'':
                raise Exception("Interrupted");

            if byte != STATUS_START1:
                continue;

            byte = s.recv(1);
            if byte == b'':
                raise Exception("Interrupted");

            if byte != STATUS_START2:
                continue;

            state = bytearray();
            while len(state) < 18:
                next = s.recv(18 - len(state));
                if next == b'':
                    raise Exception("Interrupted");

                state += next;

            if state[16] != STATUS_END1 or state[17] != STATUS_END2:
                continue;

            temp = int.from_bytes(state[0:2], byteorder='big');
            self.current_temp = temp;
            self.current_valve_pos_target = state[3];
            self.current_valve_pos_actual = state[2];

            stateVal = state[4];
            if stateVal == 0:
                self.current_state = "Bereit";
            elif stateVal == 2:
                self.current_state = "Anheizen";
            elif stateVal == 3 or stateVal == 4:
                self.current_state = "Heizbetrieb";
            elif stateVal == 7 or stateVal == 8:
                self.current_state = "Grundglut";
            elif stateVal == 97:
                self.current_state = "Heizfehler";
            elif stateVal == 98:
                self.current_state = "Tuer offen";
            else:
                self.current_state = "Unbekannter Status: " + str(state);

            break;

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the LEDATRONIC LT3 Wifi sensors."""
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)

    comm = LedatronicComm(host, port);

    LEDA_SENSORS.append(LedatronicTemperatureSensor(comm))
    LEDA_SENSORS.append(LedatronicStateSensor(comm))
    LEDA_SENSORS.append(LedatronicValveSensor(comm))
    add_entities(LEDA_SENSORS)

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
        except Exception:
            _LOGGER.error("Failed to get LEDATRONIC LT3 Wifi state.")

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
