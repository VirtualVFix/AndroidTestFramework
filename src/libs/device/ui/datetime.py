# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "Sep 18, 2017 12:54:24 PM"

from libs.core.logger import getLogger
from .base.uisettings import UISettings
from .base.constants import DEVICE_SETTINGS
from libs.device.ui.base.exceptions import DateTimeFormatError


class DateTime(UISettings):
    """ """
    def __init__(self, serial, logger=None):
        super(DateTime, self).__init__(serial, logger=logger or getLogger(__file__))
        
    def _setTimeFormatViaShell(self, time_format):
        """
        Set device time format via shell command.

        Args:
            time_format (int or string): 24 or 12

        Returns:
            True if time format was set and False otherwise
        """
        
        def command():
            self.sh('settings put system time_12_24 %s'%(time_format), errors=True, empty=True)
            out = self.sh('settings get system time_12_24', errors=True, empty=False)
            if int(out) != int(time_format):
                raise DateTimeFormatError('Time format cannot be set via shell ! \
                                           Time format do not equal: expect - %s, found - %s'%(time_format, out))

        return self._serviceCommand(command)
        
    def setTimeFormat(self, use24=False):
        """ Set time format to 24-hour if use24==True or 12 if False """
        _format = '24' if use24 else '12'
        self.logger.info('Set {}-hour time format...'.format(_format))
        if not self._setTimeFormatViaShell(_format):
            time_format = DEVICE_SETTINGS['SetTimeFormat']
            time_format['_use24'] = use24
            out = self._start(time_format)
        else: 
            out = _format
            
        if _format not in out:
            raise DateTimeFormatError('{}-hour time format cannot be set !'.format('24' if use24 else '12'))
        self.logger.done()
