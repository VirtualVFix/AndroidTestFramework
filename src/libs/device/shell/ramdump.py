# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Feb 24, 2015 12:56:06 PM$"

import os
import shutil
from time import sleep
from .base import Base
from config import CONFIG
from libs.core.logger import getLogger
from libs.device.shell.base.exceptions import DeviceLoggingError
from libs.cmd.implement.exceptions import AccessDeniedError


class Ramdump(Base):
    def __init__(self, serial, logger=None):
        super(Ramdump, self).__init__(serial, logger=logger or getLogger(__file__))

    def checkLogs(self, folder, mustfiles, allfiles=None, size=0):
        _result = ''
        if allfiles is None:
            allfiles = []

        try:
            self.logger.info('Checking "{}" logs...'.format(folder))
            if folder == 'dontpanic': # dontpanic
                _result = self.shell('ls /data/dontpanic', errors=False, empty=True)
            elif folder == 'pstore': # psstore on new devices
                try: _result = self.shell('ls /sys/fs/pstore', errors=True, empty=False)
                except Exception as e:
                    self.syslogger.exception(e)
                    if CONFIG.SYSTEM.DEBUG:
                        self.logger.exception(e)
                    self.logger.warn('Pstore log is N/A !')
                    return     
            elif folder == 'ramdump':  # ramdump
                self.logger.info('Wating for device in FASTBOOT mode...')
                self.reboot_to('fastboot', timeout=240)
                self.logger.info('Pulling ramdump logs...')
                self.fastboot('oem ramdump pull %s' % CONFIG.SYSTEM.LOG_PATH, timeout=1200, errors=False)
                _size = 0
                for subdir, dir, file in os.walk(CONFIG.SYSTEM.LOG_PATH + 'ramdump' + os.sep):
                    for f in file:
                        _size += os.path.getsize(os.path.join(subdir, f))
                        _result += f + '\n'

                if (float(_size)/1024) < size:
                    raise DeviceLoggingError('Ramdump folder size: {}Mb. Expected size: {}Mb'
                                             .format(float(_size)/1024/1024, float(size)/1024))
                self.logger.info('Total ramdump size: {}Mb. Expected size: {}Mb'
                                 .format(float(int((float(_size)/1024/1024)*100))/100, float(size)/1024),
                                 self.syslogger)
            else:
                raise DeviceLoggingError('Log type "{0}" does not support.'.format(folder))

            _tm = ''
            _count = 0
            for x in allfiles: # calc all ramdump files
                if x in _result: 
                    _count += 1
                    _tm += x + ', '
            self.logger.info('Log "{}" constaint {}/{} files: [{}]'.format(folder, _count, len(allfiles), _tm))

            _tm = []
            for x in mustfiles: # check required ramdump files
                if not x in _result: 
                    if folder == 'ramdump' and CONFIG.TEST.PROVIDED_WDRESET_VIA_FASTBOOT and x == 'kernel_log.txt':
                        self.logger.warn('Due to WDOG_AP_RESET was generated via fastboot "kernel_log.txt" file is N/A in log !')
                        continue
                    _tm.append(x)        
            if len(_tm) > 0:
                raise DeviceLoggingError('Required files are not found in "{}" log: {}'.format(folder, str(_tm)))
        except Exception as e:
            self.syslogger.exception(e)
            if CONFIG.SYSTEM.DEBUG:
                self.logger.exception(e)
            raise
        finally: 
            if os.path.exists(CONFIG.SYSTEM.LOG_PATH + 'ramdump' + os.sep) and folder == 'ramdump':
                self.logger.info('Removing local ramdump logs "{}"...'.format(CONFIG.SYSTEM.LOG_PATH + 'ramdump' + os.sep))
                shutil.rmtree(CONFIG.SYSTEM.LOG_PATH + 'ramdump' + os.sep)

    def providePanic(self, panic, skipRoot=False):
        """ provide panic WDOG_AP_RESET or AP_KERNEL_PANIC """
        if not skipRoot: self.remount()
        if panic == "WDOG_AP_RESET":
            try:
                self.logger.info('Stoping mpdecision...')
                self.shell('stop mpdecision', empty=True)
                self.logger.info('Activation all CPU...')
                self.shell('echo 0 > /sys/devices/system/cpu/cpu1/online', empty=True)
                self.shell('echo 0 > /sys/devices/system/cpu/cpu2/online', empty=True)
                self.shell('echo 0 > /sys/devices/system/cpu/cpu3/online', empty=True)
                self.logger.info('Providing WDOG_AP_RESET...')
                CONFIG.TEST.PROVIDED_WDRESET_VIA_FASTBOOT = True
                out = self.shell('echo 1 > /d/fire_watchdog_reset', timeout=10, empty=True)
                if out != '':
                    raise DeviceLoggingError('WDOG_AP_RESET error: ' + out)
            except AccessDeniedError:
                self.logger.info('AccessDenied error during providing WDOG_AP_RESET via SHELL. '
                                 'Lets try provide WDOG_AP_RESET via FASTBOOT...')
                self.logger.info('Wating for device in FASTBOOT mode...')
                self.reboot_to('fastboot', timeout=120)
                self.logger.info('Providing WDOG_AP_RESET via FASTBOOT...')
                CONFIG.TEST.PROVIDED_WDRESET_VIA_FASTBOOT = True
                out = self.fastboot('oem ramdump __trigger')
                if not 'ram dump test' in out.lower():
                    raise DeviceLoggingError('WDOG_AP_RESET error: ' + out)
            sleep(60)
        elif panic == "AP_KERNEL_PANIC":
            self.logger.info('Providing AP_KERNEL_PANIC...')
            out = self.shell('echo c > /proc/sysrq-trigger', timeout=10, empty=True)
            if out != '':
                raise DeviceLoggingError('AP_KERNEL_PANIC error: ' + out)
            sleep(30)
        else:
            raise DeviceLoggingError('Panic "{}" does not supported.'.format(panic))

        self.logger.info('Wating for device in ADB mode...')
        self.wait_for('adb', timeout=900)

    def enableRamdump(self, clear=True, stayInFastboot=False):
        """ enable ramdump """
        self.logger.info('Wating for device in FASTBOOT mode...')
        self.reboot_to('fastboot', timeout=120)
        out = self.fastboot('oem ramdump')
        if not 'ram dump is enabled' in out.lower():
            self.logger.info('Enabling RAMDUMP...')
            self.fastboot('oem ramdump enable')
            sleep(1)
            self.fastboot('oem ramdump enable')
        if clear:
            self.logger.info('Clearing RAMDUMP...')
            self.fastboot('oem ramdump clear')
        if not stayInFastboot:
            self.logger.info('Wating for device in ADB mode...')
            self.reboot_to('adb', timeout=120)
