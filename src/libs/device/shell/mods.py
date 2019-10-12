# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$11.01.2016 16:21:00$"

from .base import Base
from config import CONFIG
from libs.core.logger import getLogger


class Mods(Base):
    def __init__(self, serial, logger=None):
        super(Mods, self).__init__(serial, logger=logger or getLogger(__file__))
        self._mods_available = False
        self._mods_enabled = False
        
    def modsPrepare(self):
        # check mods available
        if CONFIG.DEVICE.MODS_ENABLE:
            try:
                self.sh('ls {}'.format(CONFIG.DEVICE.MODS_PATH), errors=True)
                self._mods_available = True
                self.logger.info('Mods is available.')
            except Exception as e:
                self.syslogger.error(e)
            self.syslogger.info('Is mods available: {}'.format(self._mods_available))
                
    def modsToggle(self, connect=False, verbose=True):
        """ connect/disconnect mod during cooling """
        try:
            if self._mods_available:
                if connect: 
                    if verbose: self.logger.info('Enabling mods...')
                    self.syslogger.info('Enabling mods...')
                    self.sh('echo {} > {}'.format(CONFIG.DEVICE.MODS_ON_OFF['on'], CONFIG.DEVICE.MODS_PATH))
                    self._mods_enabled = False
                else:
                    if verbose: self.logger.info('Disabling mods...')
                    self.syslogger.info('Disabling mods...')
                    self.sh('echo {} > {}'.format(CONFIG.DEVICE.MODS_ON_OFF['off'], CONFIG.DEVICE.MODS_PATH))
                    self._mods_enabled = False
        except Exception as e:
            self.logger.error('Mods connot be enabled/disabled: {}'.format(e), self.syslogger)
