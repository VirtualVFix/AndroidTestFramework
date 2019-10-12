# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Sep 6, 2017 12:00:00 PM$"

import re
from .base import Base
from libs.core.logger import getLogger
from libs.cmd.implement.exceptions import ResultError


class COM(Base):
    """ Operations with Charge only mode (COM) """

    def __init__(self, serial=None, logger=None):
        super(COM, self).__init__(serial, logger=logger or getLogger(__file__))

    def disableCOM(self, stay_in_fastboot=False):
        """
        Disable COM in fastboot mode

        Args:
            stay_in_fastboot (boot): Leave device in fatboot mode after COM disable
        """
        mode = self.get_mode()
        try:
            if mode == 'adb':
                self.logger.info('Rebooting device to FASTBOOT mode...')
                self.reboot_to('fastboot')
            self.wait_for('fastboot')
            self.logger.info('Disabling COM...')
            # disable via oem 
            out = self.fastboot('oem off-mode-charge disable', errors=True, empty=False)
            if not re.search('.*?off_mode_charge.*?disabled.*', out, re.I):
                raise ResultError('COM was not disabled via oem !')
            # also disable via utag
            out = self.fastboot('oem config charger_disable true', errors=True, empty=False)
            if not re.search('.*?<value>.*?(true).*?</value>.*', out.replace('\n',''), re.I):
                raise ResultError('COM was not disabled via UTAG !')
            self.logger.done()
        except ResultError as e:
            self.syslogger.exception(e)
            raise
        finally:
            if not stay_in_fastboot:
                self.logger.info('Rebooting device to ADB mode...')
                self.reboot_to('adb')
                self.wait_for('adb', timeout=160)
                self.logger.done()
