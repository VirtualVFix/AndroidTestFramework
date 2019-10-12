# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/22/17 14:23"

from abc import ABCMeta, abstractmethod


class Adb(metaclass=ABCMeta):
    """
    Class allow work with ``adb`` utility.

    Note:
        Use :mod:`src.libs.cmd.shell` module for ``adb shell``
    """

    @abstractmethod
    def __init__(self, serial=None, logger=None, **kwargs):
        """
        Args:
            logger (logging): Custom logger if need output with one logger. New logger will be created if None. (Default: None)
            serial (str): Serial number of device. May be None (Default: None)
        """

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """
        Should execute any string command
        """

    @abstractmethod
    def root(self, **kwargs) -> bool:
        """
        Request root permissions
        """

    @abstractmethod
    def remount(self, **kwargs) -> bool:
        """
        Remount
        """

    @abstractmethod
    def reboot(self, **kwargs):
        """
        Reboot device
        """

    @abstractmethod
    def reboot_bootloader(self, **kwargs):
        """
        Reboot device to bootloader
        """

    @abstractmethod
    def reboot_bl(self, **kwargs):
        """
        Reboot device to bootloader
        """

    @abstractmethod
    def pull(self, path, file, timeout, **kwargs) -> bool:
        """
        Pull file or folder from device

        Args:
            path (str): Path to file or folder on device
            file (str): Path when file or folder should be saved
            timeout (int): Timeout in seconds
        """

    @abstractmethod
    def push(self, file, path, timeout, **kwargs) -> bool:
        """
        Push file or folder to device

        Args:
            file (str): Path to file or folder
            path (str): Path on device when file or folder should be saved
            timeout (int): Timeout in seconds
        """
