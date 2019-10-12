# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "12/24/2017 1:29 PM"

from config import CONFIG
from libs.core.template import NAME
from .constants import EMULATOR_SERIAL_LIST
from .exceptions import ImplementationNotFoundError


class Factory:
    """
    Factory class to chose required feature implementation
    """

    def __init__(self, serial=None, logger=None, **kwargs):
        self.logger = logger
        self.serial = serial
        self.emulator = False
        if serial is not None and serial.strip().lower() in EMULATOR_SERIAL_LIST:
            self.emulator = True

    def __raise(self, impl, util):
        """
        Raise ImplementationNotFoundError error
        """
        raise ImplementationNotFoundError('%s of %s implementation not supported !'
                                          % (NAME.safe_substitute(name=impl), util))

    def __get_type(self, imp_type, base):
        """
        Return implementation type
        """
        _type = base
        if imp_type is None:
            if self.emulator is True:
                _type = 'emulator'
        else:
            _type = imp_type.lower()
        return _type

    def get_adb(self, imp_type=None, **kwargs):
        """
        Args:
             imp_type (str or None): Name of ADB implementation

        Allowed implementation:
            - base: Uses by default
            - wifi: ADB over WiFi (Not ready yet !)
            - tcp: ADB over TCP protocol (Not ready yet !)
            - emulator: Fake ADB bridge. Returns response on some commands specified in emulator config

        Raises:
            ImplementationNotFoundError: When implementation not found

        Returns:
            class of ADB implementation
        """
        _type = self.__get_type(imp_type, CONFIG.TEST.DEFAULT_ADB_IMPLEMENTATION)
        # base
        if _type == 'base':
            from .base.adb import Adb
            return Adb(serial=self.serial, logger=self.logger, **kwargs)
        # emulator
        elif _type in EMULATOR_SERIAL_LIST:
            from .emulator.adb import Adb as AdbFake
            return AdbFake(serial=self.serial, logger=self.logger, **kwargs)
        # wifi
        elif _type == 'wifi':
            from libs.cmd.implement.wifi.adbwifi import AdbWifi
            return AdbWifi(serial=self.serial, logger=self.logger, **kwargs)
        # tcp
        elif _type == 'tcp':
            from libs.cmd.implement.tcp.adbtcp import AdbTcp
            return AdbTcp(serial=self.serial, logger=self.logger, **kwargs)
        else:
            self.__raise(imp_type, 'ADB')

    def get_shell(self, imp_type=None, **kwargs):
        """
        Args:
             imp_type (str or None): Name of ADB shell implementation

        Allowed implementation:
            - base: Uses by default
            - wifi: ADB shell over WiFi (Not ready yet !)
            - tcp: ADB shell over TCP protocol (Not ready yet !)
            - emulator: Fake ADB shell console. Returns response on some commands specified in emulator config

        Raises:
            ImplementationNotFoundError: When implementation not found

        Returns:
            class of ADB shell implementation
        """
        _type = self.__get_type(imp_type, CONFIG.TEST.DEFAULT_SHELL_IMPLEMENTATION)
        # base
        if _type == 'base':
            from .base.shell import Shell
            return Shell(serial=self.serial, logger=self.logger, **kwargs)
        # emulator
        elif _type in EMULATOR_SERIAL_LIST:
            from .emulator.shell import Shell as ShellFake
            return ShellFake(serial=self.serial, logger=self.logger, **kwargs)
        # wifi
        elif _type == 'wifi':
            from libs.cmd.implement.wifi.shellwifi import ShellWifi
            return ShellWifi(serial=self.serial, logger=self.logger, **kwargs)
        # tcp
        elif _type == 'tcp':
            from libs.cmd.implement.tcp.shelltcp import ShellTcp
            return ShellTcp(serial=self.serial, logger=self.logger, **kwargs)
        else:
            self.__raise(imp_type, 'ADB SHELL')

    def get_fastboot(self, imp_type=None, **kwargs):
        """
        Args:
             imp_type (str or None): Name of ADB implementation

        Allowed implementation:
            - base: Uses by default
            - emulator: Fake Fastboot utility. Returns response on some commands specified in emulator config

        Raises:
            ImplementationNotFoundError: When implementation not found

        Returns:
            class of ADB implementation
        """
        _type = self.__get_type(imp_type, CONFIG.TEST.DEFAULT_FASTBOOT_IMPLEMENTATION)
        # base
        if _type == 'base':
            from .base.fastboot import Fastboot
            return Fastboot(serial=self.serial, logger=self.logger, **kwargs)
        # emulator
        elif _type in EMULATOR_SERIAL_LIST:
            from .emulator.fastboot import Fastboot as FastbootFake
            return FastbootFake(serial=self.serial, logger=self.logger, **kwargs)
        else:
            self.__raise(imp_type, 'FASTBOOT')

    def get_cmd(self, imp_type=None, **kwargs):
        """
        Args:
             imp_type (str or None): Name of ADB implementation

        Allowed implementation:
            - base: Uses by default
            - emulator: Fake CMD console. Returns response on some commands specified in emulator config

        Raises:
            ImplementationNotFoundError: When implementation not found

        Returns:
            class of ADB implementation
        """
        _type = self.__get_type(imp_type, CONFIG.TEST.DEFAULT_CMD_IMPLEMENTATION)
        # base
        if _type == 'base':
            from .base.cmd import Cmd
            return Cmd(logger=self.logger, **kwargs)
        # emulator
        elif _type in EMULATOR_SERIAL_LIST:
            from .emulator.cmd import Cmd as CmdFake
            return CmdFake(logger=self.logger, **kwargs)
        else:
            self.__raise(imp_type, 'CMD')
