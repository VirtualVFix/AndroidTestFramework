# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 04, 04 14:44:00"

import re
from .base import Base
from config import CONFIG
from libs.core.logger import getLogger
from libs.device.shell.base.constants import DUMPSYS_WAKE_LOCK
from libs.device.shell.base.constants import SUSPEND_STATE_FILE, SUSPEND_MIN_VOLTAGE_FILE, POWER_WAKE_LOCK


class Suspend(Base):
    def __init__(self, serial, logger=None):
        super(Suspend, self).__init__(serial, logger=logger or getLogger(__file__))
        # debug info
        self.__start_suspend = -1
        self.__start_vmin = -1
        # dmesg info
        self.__dmesg_timestamps = []
        
    def resetSuspendStates(self):
        self.root()
        self.__start_suspend = self._getSuspendState()
        self.__start_vmin = self._getMinVoltageState()
        if self.__start_suspend == -1 or self.__start_vmin == -1:
            self.logger.error('Suspend success status or RPM state were not reseted !')
        
    def _getSuspendState(self):
        """ get real suspend state from SUSPEND_STATE_FILE """
        out = self.shell('cat {}'.format(SUSPEND_STATE_FILE), errors=False, timeout=30)
        self.syslogger.info('Suspend stats: {}'.format(out))
        match = re.search('success:\s+([\w]+)[\n\r\t]+', out, re.IGNORECASE)
        if not match:
            self.logger.warnlist('Suspend stats cannot be got: {}'.format(out))
            return -1
        return int(match.group(1))

    def _getMinVoltageState(self):
        """ get real RPM vmin state from SUSPEND_MIN_VOLTAGE_FILE """
        out = self.shell('cat {}'.format(SUSPEND_MIN_VOLTAGE_FILE), errors=False, timeout=30)
        self.syslogger.info('RPM stats: {}'.format(out))
        match = re.search('Mode:vmin[\n\t\s\r]*count:([\d]+)[\n\t\r]+', out, re.IGNORECASE)
        if not match:
            self.logger.warnlist('RPM stats cannot be got: {}'.format(out))
            return -1
        return int(match.group(1))
   
    def getSuspendStates(self):
        """ get suspend and vmin states 
            Returns: suspend state, vmin """
        try:
            if not CONFIG.DEVICE.IS_PRODUCT_BUILD:
                self.root()
                if self.__start_suspend == -1 or self.__start_vmin == -1:
                    self.resetSuspendStates()
                success = self._getSuspendState()
                vmin = self._getMinVoltageState()
                return (self._getSuspendState()-self.__start_suspend) if success > 0 else success,\
                       (self._getMinVoltageState()-self.__start_vmin) if vmin > 0 else vmin                          
        except Exception as e:
            self.syslogger.exception(e)
            self.logger.error('Suspend states cannot be got: {}'.format(e))
        return -1, -1
        
    def getSuspendStatesDmesg(self):
        """ get suspend entry, exit, abort and suspend time from dmesg. Should work with secured builds. 
            returns: count of suspend entry, count of suspend exit, count of suspend aborting, suspend time in seconds
        """
        try:
            dmesg = self.sh('dmesg | grep suspend', errors=False, empty=True)
            dmesg = re.findall('^\[([\d.,\s]+)\]\s*(.*?)[\r\t\n]+', dmesg, re.M|re.DOTALL)            
            timestamps = []
            suspend_exit = []
            suspend_abort = []
            suspend_entry = []
            for key, text in dmesg:
                text = text.lower()
                timestamps.append(key)
                if key not in self.__dmesg_timestamps:
                    if ' suspend entry ' in text:
                        suspend_entry.append((key, text))
                    elif ' suspend exit ' in text:
                        suspend_exit.append((key, text))
                    elif ' aborting suspend' in text:
                        suspend_abort.append((key, text))   
            self.__dmesg_timestamps = timestamps
            
            _exit = 0 
            _entry = 0 
            for i in range(min(len(suspend_entry), len(suspend_exit))):
                _exit += float(suspend_exit[i][0].replace(',',''))
                _entry += float(suspend_entry[i][0].replace(',',''))
            total_time = abs(_exit-_entry)
                
            return len(suspend_entry), len(suspend_exit), len(suspend_abort), float(int(total_time*100))/100
        except Exception as e:
            self.syslogger.exception(e)
            self.logger.error('Suspend states cannot be got in dmesg: {}'.format(e))
        return 0, 0, 0, 0
    
    def getSuspendBlockers(self):
        """ returns suspend blockers from dumpsys or empty list """
        res = []
        try:
            out = self.sh(DUMPSYS_WAKE_LOCK, errors=False, remove_line_symbols=True)
            match = re.search('suspend blockers:\s+size=[\d]+\s*(.*)display\s', out.replace('\n',' '), re.I)
            if match:
                res = [(x.strip(),y) for x,y in re.findall('(.*?):\sref count=([\d]+)', match.group(1), re.I)]
        except Exception as e:
            self.syslogger.exception(e)
            self.logger.error('Suspend blockers cannot be got: {}'.format(e))
        return res
    
    def getWakeLocks(self):
        """ returns wake locks from dumpsys or empty list """
        res = []
        try:
            out = self.sh(DUMPSYS_WAKE_LOCK, errors=False, remove_line_symbols=True)
            match = re.search('wake locks:\s+size=[\d]+\s*(.*)suspend\s', out.replace('\n',' '), re.I)
            if match:
                res = [y.strip()+')' for y in ' '.join([x for x in match.group(1).decode('utf-8')
                                                       .split()]).split(')') if y.strip() != '']
        except Exception as e:
            self.syslogger.exception(e)
            self.logger.error('Suspend blockers cannot be got: {}'.format(e))
        return res
    
    def getPowerWakeLock(self):
        """ return value from /sys/power/wake_lock if available or '' """
        res = []
        try:
            if not CONFIG.DEVICE.IS_PRODUCT_BUILD:
                self.root()
                out = self.sh('cat '+ POWER_WAKE_LOCK, errors=False, empty=True, remove_line_symbols=True)
                res = [x.strip() for x in out.split('\n') if x.strip() != '']
        except Exception as e:
            self.syslogger.exception(e)
            self.logger.error('Power lock cannot be got: {}'.format(e))
        return res
