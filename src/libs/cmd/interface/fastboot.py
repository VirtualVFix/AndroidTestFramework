# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/22/17 14:23"

from abc import ABCMeta, abstractmethod


class Fastboot(metaclass=ABCMeta):
    """
    Abstract class to work with ``fastboot`` utility.
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
        Call class as ``self.fastboot`` function
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
