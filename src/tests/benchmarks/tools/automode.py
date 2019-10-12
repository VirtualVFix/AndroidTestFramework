# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Jul 6, 2016 12:50:47 PM$"

import re
import pytz
import datetime
from config import CONFIG
from libs.cmd import Manager
from libs.core.logger import getLogger
from libs.automode import AutoBenchmarks


class AutoMode(AutoBenchmarks, Manager):
    def __init__(self, serial, spreadsheet_id, sheet_identifier, client_file_name):
        Manager.__init__(self, serial, logger=getLogger(__file__))
        AutoBenchmarks.__init__(self, spreadsheet_id, sheet_identifier, client_file_name, logger=getLogger(__file__))
        
    def updateHeaderConfig(self):
        """ Update defaule values of "self.header_config" to actual values """
        def addHeaderValue(index, value):
            if len(self.header_config[index]) > 3: 
                self.header_config[index][3] = value
            else: self.header_config[index][3].append(value)
            
        # check if header exists
        data_range = [x[0]+1 for x in self.header_config]
        if not self.sheet_header_rewrite: 
            current_header = self.getValues('{0}1:{0}{1}'.format(self.convertIndexToName(self.sheet_results_column),
                                                                 max(data_range)))
        else:
            current_header = [None for _ in range(max(data_range))]
            
        # update header
        for i in range(len(self.header_config)):
            name = self.header_config[i][2].lower()
            if 'build' in name:
                tm = '{0} {1}\n{2}'.format(self.prop.getDeviceName().capitalize(),
                                           self.prop.getRevisionHW().upper(),
                                           self.prop.getBuildDescription().split(',')[0].replace(' ','_'))
                addHeaderValue(i, tm)
            elif 'date' in name:
                current_date = datetime.datetime.now(pytz.timezone(CONFIG.SYSTEM.TIMEZONE))
                addHeaderValue(i, datetime.datetime(current_date.year, current_date.month, current_date.day, 0, 0))
            elif 'barcode' in name:
                addHeaderValue(i, self.serial.upper())
            elif 'storage' in name:
                # skip phone reboot if header exists
                if current_header[self.header_config[i][0]] is None:
                    # self.logger.info('Rebooting device to FASTBOOT mode...')
                    self.reboot_to('fastboot', verbose=True)
                    self.wait_for('fastboot', verbose=True)
                    self.prop.update_cache()
                    addHeaderValue(i, self.prop.getEMMC().upper())
                    # self.logger.info('Rebooting device to Idle...')
#                    self.fastboot('oem fb_mode_clear')
                    self.reboot_to('adb', verbose=True)
                    self.wait_idle(verbose=True)
            elif 'cpu' in name: 
                revision = self.sh('cat /proc/cpuinfo | grep Revision')
                match = re.search(':\s([\w]+)', revision, re.I)
                addHeaderValue(i, match.group(1) if match else 'N/A')
            elif 'bsp' in name: 
                if len(self.header_config[i]) < 3 or self.header_config[i][3] is None:
                    addHeaderValue(i, 'Your Ad Could Be Here !')
        
        # update header    
        self.updateHeader(self.header_config, self.convertIndexToName(self.sheet_results_column),
                          current_header=current_header, rewrite=self.sheet_header_rewrite)
