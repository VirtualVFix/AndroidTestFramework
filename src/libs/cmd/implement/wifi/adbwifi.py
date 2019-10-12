# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/22/17 14:26"

from libs.cmd.implement.base.base import Base
from libs.core.tools import NotImplemented
from libs.cmd.interface.adb import Adb as AdbInt


@NotImplemented
class AdbWifi(Base, AdbInt):
    """
    ``adb`` utility via WiFi

    Warning:
        Feature not implements yet !
    """

    def __init__(self, logger=None, serial=None, **kwargs):
        """
        Args:
            logger (logging): Custom logger if need output with one logger. New logger will be created if None. (Default: None)
            serial (str): Serial number of device. May be None (Default: None)
        """
        super(AdbWifi, self).__init__(logger=logger, serial=serial, **kwargs)

    def __call__(self, *args, **kwargs):
        """
        Call class as ``self.adb`` function

        Returns:
            func: self.adb(`*args`, `**kwargs`)
        """

    def adb(self, command, **kwargs) -> str:
        """
        Execute any ``adb`` command.

        Args:
            command (str): Command to execute without ``adb -s SERIAL``
            timeout (int, optional): Command timeout
            error (bool, optional): Check errors in command output
            empty (bool, optional): Check if command output is empty

        Returns:
             str: output

        Raises:
            Exception: if exception type not specified
            TimeoutExpired: if command ``timeout`` expired
            EmptyOutputError: if ``empty`` == True and command output is empty.
        """
        out = ''
        timeout, error, empty = self._get_arguments(**kwargs)
        return out

    def root(self, **kwargs) -> bool:
        """
        Request root permissions
        """

    def remount(self, **kwargs) -> bool:
        """
        Remount
        """

    def reboot(self, **kwargs):
        """
        Reboot device
        """

    def reboot_bootloader(self, **kwargs):
        """
        Reboot device to bootloader
        """

    def reboot_bl(self, **kwargs):
        """
        Reboot device to bootloader
        """

    def pull(self, path, file, **kwargs) -> bool:
        """
        Pull file or folder from device

        Args:
            path (str): Path to file or folder on device
            file (str): Path when file or folder should be saved
            timeout (int): Timeout in seconds
        """

    def push(self, file, path, **kwargs) -> bool:
        """
        Push file or folder to device

        Args:
            file (str): Path to file or folder
            path (str): Path on device when file or folder should be saved
            timeout (int): Timeout in seconds
        """
