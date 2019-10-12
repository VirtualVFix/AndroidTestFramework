# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Jun 29, 2015 12:28:10 PM$"

import re
from .base import Base
from config import CONFIG
from libs.core.logger import getLogger


class Dmesg(Base):
    """ Dmesg logs oparations """

    def __init__(self, serial, logger=None):
        super(Dmesg, self).__init__(serial, logger=logger or getLogger(__file__))
        self.timecodes = []
        
    def dmesg(self, msg):
        result = []
        try:
            out = re.findall('(\[[\d\s,.]+\])[\s]*(('+ ('|'.join(x for x in msg) if isinstance(msg, list) else msg) +').*?)\n', self.sh('dmesg', errors=False, empty=True), re.DOTALL|re.IGNORECASE)
            for timecode, message, ms in out:
                if not timecode.lower() in self.timecodes:
                    self.timecodes.append(timecode.lower())
                    self.syslogger.warn(timecode + message.replace('\r','').replace('\t',''))
                    result.append((timecode, message.replace('\r','').replace('\t',''), ms))
        except Exception as e:
            self.syslogger.exception(e)
            if CONFIG.SYSTEM.DEBUG:
                self.logger.exception(e)

        if len(result) > 0:
            return result
        return None
