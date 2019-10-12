# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "Sep 18, 2017 12:54:13 PM"

from libs.core.logger import getLogger
from .base.uisettings import UISettings
from .base.constants import DEVICE_SETTINGS
from libs.device.ui.base.exceptions import SecuritySetingsError


class Security(UISettings):
    def __init__(self, serial, logger=None):
        super(Security, self).__init__(serial, logger=logger or getLogger(__file__))
        
    def setScreenLockToNone(self):
        """ set stay awake debug option """
        self.logger.info('Set screen lock to None...')
        security = DEVICE_SETTINGS['SetScreenLockToNone']
        out = self._start(security)
        
        if 'none' not in out.lower():
            raise SecuritySetingsError('Security cannot be set to None !')
        self.logger.info(out)
        self.logger.done()
