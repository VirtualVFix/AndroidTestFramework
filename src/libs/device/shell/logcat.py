# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Aug 12, 2015 3:17:27 PM$"

import os
from .base import Base
from config import CONFIG
from libs.core.logger import getLogger


class Logcat(Base):
    def __init__(self, serial, logger=None):
        super(Logcat, self).__init__(serial, logger=logger or getLogger(__file__))
        
    def logcatClear(self):
        if CONFIG.TEST.LOG_COLLECTION:
            self.syslogger.info('Clear logcat: {}'.format(self.sh('logcat -c')))
        
    def logcatCollection(self):
        # logs collection
        if CONFIG.TEST.LOG_COLLECTION:
            log_dir = CONFIG.SYSTEM.LOG_PATH + 'logcat' + os.sep
            if not os.path.exists(log_dir): os.mkdir(log_dir)
            logfile = log_dir + CONFIG.TEST.TEST_NAME + '_{}_{}_logcat.log'.format(CONFIG.TEST.CURRENT_SUITE,
                                                                                   CONFIG.TEST.CURRENT_CYCLE)
            with open(logfile, 'ab') as file:
                file.write(self.sh('logcat -d', errors=False))
                self.syslogger.info('Logcat saved to {}'.format(logfile))
