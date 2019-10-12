# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Sep 24, 2015 3:51:45 PM$"

import re
from .base import Base
from libs.core.logger import getLogger
from libs.cmd.implement.exceptions import AccessDeniedError


class SDCard(Base):
    def __init__(self, serial, logger=None):
        super(SDCard, self).__init__(serial, logger=logger or getLogger(__file__))

    def detectSDCard(self, storage='/mnt/media_rw/'):
        try:
            self.root()
            try:
                out = self.sh('df')
            except AccessDeniedError:
                self.remount()
                out = self.sh('df')

            self.syslogger.info(out)
            if storage in out:
                path = re.findall(storage + '([\w_-]+)', out, re.DOTALL|re.IGNORECASE)
                for x in path:
                    if x.lower() != 'emulated': 
                        res = storage + x + '/'
                        self.logger.info('SD card path: [{}]'.format(res), self.syslogger)
                        return res
        except Exception as e:
            self.syslogger.exception(e)
        self.syslogger.info('SD card not found.')
        return None
