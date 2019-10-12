# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Sep 24, 2015 3:51:45 PM$"

import re
from .base import Base
from libs.core.logger import getLogger
from libs.device.shell.base.constants import MEMORY_MEASURE_UNITS


class Memory(Base):
    def __init__(self, serial, logger=None):
        super(Memory, self).__init__(serial, logger=logger or getLogger(__file__))

    def getMemory(self, tag='memfree', unit='Gb'):
        """ 
        Return memory status from "/proc/meminfo"
        
        Args: 
            tag (str): Line from meminfo file
            unit (str): Should be in ['b', 'Kb', 'Mb, 'Gb', ...]. Mesure units for memory
        """
        
        try:
            out = self.sh('cat /proc/meminfo')
            match = re.search(tag + ':[\s\r\t]+([\d]+)[\s\r\t]+([\w]+)[\r\t\n]+', out, re.I|re.M|re.DOTALL)
            if not match:
                return -1
            
            size = float(match.group(1))
            measure = match.group(2).upper()
            
            # convert to requered units
            if unit.upper() != measure:
                _ind_reqired = MEMORY_MEASURE_UNITS.index(unit.upper())
                _ind_current = MEMORY_MEASURE_UNITS.index(measure)
                if _ind_reqired < _ind_current:
                    for i in range(_ind_current-_ind_reqired):
                        size *= 1024
                else:
                    for i in range(_ind_reqired-_ind_current):
                        size /= 1024
            return size
        except Exception as e:
            self.syslogger.exception(e)
        return -1
