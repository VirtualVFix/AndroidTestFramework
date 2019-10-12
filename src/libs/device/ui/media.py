# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "Sep 18, 2017 12:16:46 PM"

from config import CONFIG
from libs.core.logger import getLogger
from .base.uisettings import UISettings
from .base.constants import DEVICE_SETTINGS


class Media(UISettings):
    def __init__(self, serial, logger=None):
        super(Media, self).__init__(serial, logger=logger or getLogger(__file__))
        
    def muteMediaVolume(self):
        """
        Mute media volume on device
        """
        try:
            self.logger.info('Mute media volume...')
            media = DEVICE_SETTINGS['MediaVolume']
            self._start(media)
            self.logger.done()
        except Exception as e:
            self.syslogger.exception(e)
            if CONFIG.SYSTEM.DEBUG:
                raise
            self.logger.error('Media value cannot be muted due to error: %s' % e)
