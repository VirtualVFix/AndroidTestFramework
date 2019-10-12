# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/22/17 14:23"

from .adb import Adb
from libs.cmd.interface.shell import Shell as ShellImp


class Shell(Adb, ShellImp):
    """
    Class to work with ``adb shell`` utility.

    See also:
        :mod:`src.libs.cmd.adb` module
    """

    def __init__(self, serial=None, logger=None, **kwargs):
        """
        Args:
            logger (logging): Custom logger if need output with one logger. New logger will be created if None. (Default: None)
            serial (str): Serial number of device. May be None (Default: None)
        """
        super(Shell, self).__init__(logger=logger, serial=serial, **kwargs)

    def __call__(self, command, **kwargs):
        """
        Execute any ``adb shell`` command.

        Args:
            command (str): Str command to execute (without **adb -s SERIAL shell**)

        Kwargs:
            timeout (int, optional): Command timeout
            error (bool, optional): Check errors in command output
            empty (bool, optional): Check if command output is empty

        Returns:
             str: output or ''
        """
        cmd = 'shell "%s"' % command
        return super(Shell, self).__call__(cmd, **kwargs)

    def is_device_alive(self, **kwargs) -> bool:
        """
        Check if device available
        """
        try:
            return self.__call__('echo ok', remove_line_symbols=True).strip().lower() == 'ok'
        except:
            return False
