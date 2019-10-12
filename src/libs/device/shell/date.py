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
from libs.device.shell.base.exceptions import SyncDateError


class Date(Base):
    """ Operations with device date and time """

    def __init__(self, serial=None, logger=None):
        super(Date, self).__init__(serial, logger=logger or getLogger(__file__))

    def syncDate(self):
        """
        Sync device date and time.
        Default device SET format is MMDDhhmm[[CC]YY][.ss]
        """
        try:
            mode = self.get_mode()
            if mode == 'fastboot':
                self.logger.error('Device date cannot be synchronized in FASTBOOT mode !')
                return

            self.logger.info('Synchronizing date and time on device...')
            # set timezone
            self.root(verbose=False)
            self.sh('setprop persist.sys.timezone %s'
                    % CONFIG.SYSTEM.TIMEZONE, errors=False, empty=True, __emulator_command_response__='')
            # set time
            now = datetime.datetime.now(pytz.timezone(CONFIG.SYSTEM.TIMEZONE))
            cmd = 'date %02d%02d%02d%02d%d.%02d' % (now.month, now.day, now.hour, now.minute, now.year, now.second)

            # Add "__emulator_command_response__" to command to avoid error with emulator
            out = re.sub('[\t\r\n]+', ' ', self.sh(cmd, errors=True, empty=False,
                                                   __emulator_command_response__='pass'))
            if 'bad date' in out.lower():
                raise SyncDateError(out)
            
            out = re.sub('[\t\r\n]+', ' ', self.sh('date', errors=True, empty=False,
                                                   __emulator_command_response__=
                                                   now.strftime('%a %b %d %H:%M:%S CDT %Y')))
            date = [str(x) for x in out.lower().split()]
            cur_time = date[3].split(':')

            # verify date
            _month = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
            if (now.day != int(date[2])) \
                    or (now.month != _month.index(date[1])+1) \
                    or (now.hour != int(cur_time[0])) \
                    or (now.minute != int(cur_time[1])) \
                    or (now.second != int(cur_time[2])) \
                    or (now.year != int(date[5])):
                raise SyncDateError('Date sync error: sent - "%s", found - "%s"'
                                    % (now.strftime('%a %b %d %H:%M:%S %Y'),
                                       ' '.join([str(date[x]).capitalize() for x in range(len(date)) if x != 4])))
        
            self.logger.info('Current date: %s' % now.strftime('%a %b %d %H:%M:%S %Y'))
            self.logger.info('Device date: %s' % ' '.join([str(date[x]).capitalize()
                                                           for x in range(len(date)) if x != 4]))

            # sync internal time
            self.sh('am broadcast -a android.intent.action.TIME_SET', errors=True, empty=False)
            self.logger.done()
        except Exception as e:
            self.syslogger.exception(e)
            if CONFIG.SYSTEM.DEBUG:
                self.logger.exception(e)
            self.logger.error(e)
