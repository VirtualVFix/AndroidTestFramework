# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Sep 6, 2017 12:00:00 PM$"

import re
import pytz
import datetime
from .base import Base
from config import CONFIG
from libs.core.logger import getLogger


class Display(Base):
    """ Operations with device display """
    def __init__(self, serial=None, logger=None):
        super(Display, self).__init__(serial, logger=logger or getLogger(__file__))

    def getScreenResolution(self):
        """ get display resolution 
            returns: int(max), int(min) or None, None """
        try:
            dumpsys = self.sh('dumpsys SurfaceFlinger', errors=False, empty=False)
            match = re.findall('Display\[[\d]+\].*[\s\r\t]*\*\s\d:\s([\dx]+)', dumpsys, re.I|re.M)
            if len(match) > 0: 
                self.syslogger.info(match)
                match = [int(x) for x in match[0].split('x')]
                return max(match), min(match)
        except Exception as e:
            self.syslogger.exception(e)
        return None, None
    
    def isScreenOn(self):
        """ Check if screen is ON """
        try:
            dumpsys = self.sh('dumpsys display', errors=False, empty=False)
            match = re.search('display\spower\sstate:[\s\r\t]+mScreenState\s*=\s*(on|off).*', dumpsys,
                              re.DOTALL|re.I|re.M)
            return (match is not None) & (match.group(1).lower() == 'on')
        except Exception as e:
            self.syslogger.exception(e)
        return False
    
    def turnScreenOnAndUnlock(self, verbose=False):
        """ Turn display ON and unlock """
        if not self.isScreenOn():
            if verbose:
                self.logger.info('Turn display ON')
            self.sh('input keyevent KEYCODE_POWER; sleep 0.2; input keyevent KEYCODE_MENU')
    
    def turnScreenOff(self, verbose=False):
        """ Turn screen OFF """
        if self.isScreenOn():
            if verbose:
                self.logger.info('Turn display OFF')
            self.sh('input keyevent KEYCODE_POWER')
    
    def takeScreenshot(self, name, replace=True, screencap='/system/bin/screencap', path='/data/local/tmp/'):
        """ 
        Take screenshot and save it on device 
        
        Args:
            replace (bool, default False): replace already exists files
            screencap (str): path to screencap utility on device
            path (str): path to save screenshot on device            
        
        Returns: 
            (screenshot name, path to screenshot folder)
        """
        path = path if path.endswith('/') else '%s/' % path  # path to keep screenshot on device
        
        if replace is False:
            # generate unique name
            name = '%s_%s.png' % (name[:-4],
                                  datetime.datetime.now(pytz.timezone(CONFIG.SYSTEM.TIMEZONE))
                                  .strftime('_%m%d%y%H%M%S%f'))
        else:
            name = name if name.endswith('.png') else '%s.png' % name
            
        _path = '%s%s' % (path, name)
        self.sh('%s -p %s' % (screencap, _path), errors=True, empty=True)
        return name, path

    def setScreenBrightness(self, value, path='/sys/class/leds/lcd-backlight/brightness'):
        """ Set screen brightness via shell """
        self.sh('echo %d > %s' % (value, path), errors=True, empty=True)
