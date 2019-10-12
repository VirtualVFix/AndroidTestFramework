# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/22/17 14:27"

import re
from .cmd import Cmd
from ..gurads import BaseGuard
from libs.cmd.interface.fastboot import Fastboot as FbInt


class Fastboot(Cmd, FbInt):
    """
    Class to work with ``fastboot`` utility.
    """

    def __init__(self, serial=None, logger=None, **kwargs):
        """
        Args:
            logger (logging): Custom logger if need output with one logger. New logger will be created if None. (Default: None)
            serial (str): Serial number of device. May be None (Default: None)
        """
        super(Fastboot, self).__init__(logger=logger, serial=serial, **kwargs)

    @BaseGuard
    def __call__(self, command, barecmd=False, **kwargs):
        """
        Execute any ``fastboot`` command.

        Args:
            *args (str): Separated command to execute (without **fastboot -s SERIAL**)
            barecmd (bool): Execute Fastboot command with out serial number included

        Kwargs:
            timeout (int, optional): Command timeout
            error (bool, optional): Check errors in command output
            empty (bool, optional): Check if command output is empty

        Returns:
             str: output or ''
        """
        kwargs = self.update_base_kwargs(**kwargs)
        cmd = ('fastboot -s %s %s' % (self.serial, command)) \
            if self.serial is not None and not barecmd else ('fastboot %s' % command)
        return super(Fastboot, self).__call__(cmd, **kwargs)

    def devices(self, **kwargs):
        """
        Get fastboot devices

        Returns:
            ([barcode], [status]): list of barcodes with list of statuses
        """
        out = self.__call__('devices', barecmd=True, **kwargs)
        dev = re.findall('([\d\w]+)\t([\w]+)', out, re.I)
        return [x[0].upper() for x in dev], [x[1].lower() for x in dev]

    def reboot(self, **kwargs):
        """
        Reboot device to ADB
        """
        self._current_mode = None
        self.__call__('reboot', **kwargs)

    def reboot_bootloader(self, **kwargs):
        """
        Reboot device to bootloader
        """
        self._current_mode = None
        self.__call__('reboot-bootloader', **kwargs)

    def reboot_bl(self, **kwargs):
        """
        Reboot device to bootloader
        """
        self.reboot_bootloader(**kwargs)
