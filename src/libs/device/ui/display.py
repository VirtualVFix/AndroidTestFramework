# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "Sep 18, 2017 12:14:30 PM"

import re
from libs.core.logger import getLogger
from .base.uisettings import UISettings
from libs.device.ui.base.exceptions import DisplaySetingsError
from .base.constants import DEVICE_SETTINGS, DISPLAY_TIMEOUT_ALLOW_UNITS
from .base.constants import MAX_DISPLAY_TIMEOUT_IN_SECONDS, MIN_DISPLAY_TIMEOUT_IN_SECONDS


class Display(UISettings):
    def __init__(self, serial, logger=None):
        super(Display, self).__init__(serial, logger=logger or getLogger(__file__))
        
    def _setDisplayTimeoutViaShell(self, timeout):
        """
        Set device display timeout via shell command.

        Args:
            timeout (int): Timeout in seconds

        Returns:
            True if timeout was set and False otherwise
        """

        def command():
            self.sh('settings put system screen_off_timeout %d'%(timeout*1000), errors=True, empty=True)
            out = self.sh('settings get system screen_off_timeout', errors=True, empty=False)
            if int(out) != timeout*1000:
                raise DisplaySetingsError('Timeout cannot be set via shell ! \
                                          Timeout do not equal: expect - %d, found - %s'%(timeout*1000,out))
                                  
        return self._serviceCommand(command)
        
    def setMaxDisplayTimeout(self):
        """
        Set up display timeout to maximum
        """
        self.logger.info('Configure display timeout...')
        if not self._setDisplayTimeoutViaShell(MAX_DISPLAY_TIMEOUT_IN_SECONDS):
            screen = DEVICE_SETTINGS['MaxDisplayTimeout']
            out = self._start(screen)
        else:
            out = '%d minutes'%(MAX_DISPLAY_TIMEOUT_IN_SECONDS/60)
        self.logger.info('Display timeout was set to "{}"'.format(out))
        self.logger.done()
        
    def setSpecifiedDisplayTimeout(self, timeout_with_units):
        """
        Set display timeout.

        Args:
            timeout_with_units (str): Timeout with units (like: "15 seconds" or "30 min")

        Note:
            Allowed following units: **sec**, **second**, **seconds**, **min**, **minute**, **minutes**
        """
        match = re.search('([\d]+)\s*('+'|'.join(DISPLAY_TIMEOUT_ALLOW_UNITS)+'{1})', timeout_with_units)
        if not match: 
            raise DisplaySetingsError('"{}" unsupported display timeout format.'.format(timeout_with_units))
        
        _time = int(match.group(1))
        _unit = match.group(2).lower()
        self.logger.info('Configuring display timeout to "{} {}"...'.format(_time, _unit))
        if not self._setDisplayTimeoutViaShell(_time*60*60 if _unit[:1]=='h' \
                                               else _time*60 if _unit[:1]=='m' \
                                               else _time if _unit[:1]=='s' \
                                               else MIN_DISPLAY_TIMEOUT_IN_SECONDS):
            screen = DEVICE_SETTINGS['SetDisplayTimeout']
            screen['_timeout'] = _time
            screen['_unit'] = _unit
            out = self._start(screen)

            if 'not found' in out.lower() or out == '':
                raise DisplaySetingsError('Display timeout {} {} cannot be selected !'.format(_time, _unit))
        else:
            out = '%d %s'%(_time, _unit)        
        
        self.logger.info('Display timeout was set to "{}"'.format(out))
        self.logger.done()
        return out
