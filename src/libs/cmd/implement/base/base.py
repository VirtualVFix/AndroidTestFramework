# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/26/17 12:03"

from libs.core.logger import getSysLogger, getLogger
from libs.cmd.implement.constants import DEFAULT_COMMAND_TIMEOUT


class Base:
    """
    Base class for ``adb``, ``shell`` and ``fastboot`` implementations
    """

    def __init__(self, serial=None, logger=None, **kwargs):
        """
        Args:
            logger (logging): Custom logger if need output with one logger. New logger will be created if None. (Default: None)
            serial (str): Serial number of device. May be None (Default: None)
        """
        self.logger = logger or getLogger(__file__)
        self.syslogger = getSysLogger()
        self.__serial = serial
        # Current mode. Used to fasted execute commands with out excess delays in same operations like "wait for device"
        # Variables should be None when device reboots
        self._current_mode = None

    @property
    def saved_mode(self):
        """
        Current device mode. Used to fasted execute commands with out excess delays in same operations
        like "wait for device"

        Returns:
            str or None: self._current_mode or None if mode was not set
        """
        return self._current_mode

    @property
    def serial(self):
        """
        Device serial number property

        Returns:
             (str): device serial number or None
        """
        return self.__serial

    @serial.setter
    def serial(self, value):
        """
        Device serial number setter

        Args:
             serial(str): device serial number or None
        """
        self.__serial = value

    @staticmethod
    def update_base_kwargs(**kwargs) -> dict:
        """
        Check base arguments and update it with default values if required.

        Base args:
            timeout (int): Command timeout in seconds (Default: 120)
            error (bool): Check error in command result output (Default: True)
            empty (bool): Check if command result output may be empty (Default: True)

        Returns:
            updated kwargs

        Note:
            Also available following aliases for function arguments:
            **time** instead ``timeout``;
            **checkError** and **checkErrors** instead ``error``;
            **canBeEmpty** instead ``empty``.

        Warning:
            Aliases added for backward compatibility and not recommended to use !
        """
        kwargs['timeout'] = kwargs.get('timeout', None) \
            or kwargs.get('time', None) \
            or DEFAULT_COMMAND_TIMEOUT
        kwargs['errors'] = kwargs.get('error', None) \
            or kwargs.get('errors', None) \
            or kwargs.get('checkError', None) \
            or kwargs.get('checkErrors', None) \
            or True
        kwargs['empty'] = kwargs.get('empty', None) \
            or kwargs.get('canBeEmpty', None) \
            or True
        # print('BASE ARGS: ', kwargs)
        return kwargs
