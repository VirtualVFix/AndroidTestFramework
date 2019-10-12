# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/27/17 14:58"

from .base import Base
from libs.core.register.base.exceptions import ConfigError


class Device(Base):
    """
    Device default config. This config is part of :class:`src.libs.core.register.Register`
    """
    #: Build type user, userdebug or release
    BUILD_TYPE = ''
    #: Build version
    BUILD_VERSION = ''
    #: Build release
    BUILD_RELEASE = ''
    #: Build product name
    BUILD_PRODUCT = ''
    #: Device name
    DEVICE_NAME = ''
    #: Device product name
    DEVICE_PRODUCT = ''
    #: CPU HW name
    CPU_HW = ''
    #: Bit CPU
    CPU_64_BIT = False
    #: is device flashed with product build
    IS_PRODUCT_BUILD = None
    #: Build fingerprint
    BUILD_FINGERPRINT = ''

    #: Enable battery control ("--disable-battery-control" option)
    BATTERY_CONTROL = True
    #: Battery level thresholds ("--battery-levels" option)
    BATTERY_CONTROL_LEVELS = [70, 90]

    #: Enable temperature control ("--disable-temperature-control" option)
    ENABLE_TEMPERATURE_CONTROL = True
    #: Thermal sensors for temperature control. Sensors are selected automatically by device platform.
    #: Sensor from 'default' sector will be used If platform is not specified.
    THERMAL_SENSOR = {'default': None}
    #: Sleep time for temperature control if thermal sensor is N/A in THERMAL_SENSOR variable.
    SLEEP_TIME_WITHOUT_SENSOR = 300
    #: Cooling timeout. Test starts if cooling timeout expired.
    COOLING_TIMEOUT = 600
    #: Maximal temperature when test can be started with temperature control enabled.
    #: Temperature is selected automatically by device product name.
    #: Temperature from 'default' sector will be used If product name is not specified.
    RUN_TEMPERATURE = {'default': 40}

    #: Enable mods if available. Use "--enable-mods" launch options
    MODS_ENABLE = False
    #: Path for on/off mods
    MODS_PATH = '/sys/class/display/display0/notify'
    #: Command for on/off mods
    MODS_ON_OFF = {'on': 'connect', 'off': 'disconnect'}

    def __init__(self):
        super(Device, self).__init__()
        # serial number
        self.__serial = None

    @property
    def SERIAL(self):
        """
        Device serial number property.

        Returns:
            str: serial number or None
        """
        return self.__serial

    @SERIAL.setter
    def SERIAL(self, value):
        """
        Device serial number setter.

        Warning:
            Device serial number may be set only once and cannot be changed after initialization

        Args:
             value (str): Serial number
        """
        if self.__serial is not None:
            raise ConfigError('Device Serial number cannot be changed after initialization !')

        self.__serial = value
