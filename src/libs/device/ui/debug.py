# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "Sep 18, 2017 12:53:10 PM"

from libs.core.logger import getLogger
from .base.uisettings import UISettings
from .base.constants import DEVICE_SETTINGS
from libs.device.ui.base.exceptions import DebugSetingsError


class Debug(UISettings):
    def __init__(self, serial, logger=None):
        super(Debug, self).__init__(serial, logger=logger or getLogger(__file__))

    def setStayAwake(self, enable=True):
        """ set stay awake debug option """
        self.logger.info('{} Stay awake option...'.format('Enable' if enable else 'Disable'))
        awake = DEVICE_SETTINGS['SetStayAwake']
        awake['_enable'] = enable
        out = self._start(awake)
        
        if not ('enabled' if enable else 'disabled') in out.lower():
            raise DebugSetingsError('Stay awake option cannot be {} !'.format('enabled' if enable else 'disabled'))
        self.logger.info(out)
        self.logger.done()
