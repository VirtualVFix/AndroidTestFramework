# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Sep 6, 2017 12:00:00 PM$"

import re
import os
from .base import Base
from config import CONFIG
from libs.core.logger import getLogger
from libs.cmd.implement.exceptions import ResultError
from libs.device.shell.base.exceptions import DeviceLoggingError


class Logs(Base):
    """ Operation with device logs """
    def __init__(self, serial=None, logger=None):
        super(Logs, self).__init__(serial, logger=logger or getLogger(__file__))

    def collectAplogcatLogs(self):
        """ Collect aplogcat logs """
        self.root()
        self.wait_for('adb', timeout=60)
        self.sh('mkdir /cache/tmp')
        self.logger.info('Collecting aplogcat logs...')
        out = self.sh('aplogcat -d -o /cache/tmp/ -n 1', errors=True, empty=False)
        if 'aplogd is not enabled' in out: 
            raise DeviceLoggingError('Aplogd is not enabled !')

        logdir = '%s aplogcat_%s_%s_%s_%s%s' % (CONFIG.SYSTEM.LOG_PATH,
                                                CONFIG.TEST.CURRENT_STATE.replace(' ', '_').split('|')[0],
                                                CONFIG.TEST.CURRENT_SUITE,
                                                CONFIG.TEST.CURRENT_CYCLE,
                                                CONFIG.TEST.LOCAL_CURRENT_CYCLE,
                                                os.sep)
        if not os.path.exists(logdir):
            os.mkdir(logdir)

        self.logger.info('Pulling aplogcat logs...')
        self.pull('/cache/tmp/', logdir)
        with open(logdir + 'dmesg.log', 'a') as file:
            file.write(self.sh('dmesg', errors=False, timeout=60))
        self.logger.done()
        self.logger.info('Aplogcat logs saved in "{}"'.format(logdir), self.syslogger)
        
    def clearRamdump(self, stay_in_fastboot=False):
        """ clean ramdump logs """
        mode = self.get_mode()
        try:
            if mode == 'adb':
                self.logger.info('Rebooting device to FASTBOOT mode...')
                self.reboot_to('fastboot')
            self.wait_for('fastboot')
            self.logger.info('Clearing Ramdump...')
            out = self.fastboot('oem ramdump clear', errors=True, empty=False)
            if not re.search('.*?OKAY.*', out, re.I):
                raise ResultError('Ramdump cannot be clear !')
            self.logger.done()
        except ResultError as e:
            self.syslogger.exception(e)
            raise
        finally:
            if not stay_in_fastboot:
                self.logger.info('Rebooting device to ADB mode...')
                self.reboot_to('adb')
                self.wait_for('adb', timeout=160)
                self.logger.done()
                
    def disableSerialConsole(self, stay_in_fastboot=False):
        """ disable serial consol via utag in fastboot """
        mode = self.get_mode()
        try:
            if mode == 'adb':
                self.logger.info('Rebooting device to FASTBOOT mode...')
                self.reboot_to('fastboot')
            self.wait_for('fastboot')
            self.logger.info('Disabling serial console...')
            out = self.fastboot('oem config console disable', errors=False, empty=False)
            match = re.search('<value>.*?(false|disable).*?</value>', out.replace('\n',''), re.I)
            if not match:
                raise ResultError('Serial console cannot be disabled !')
            self.logger.done()
        except ResultError as e:
            self.syslogger.exception(e)
            raise
        finally:
            if not stay_in_fastboot:
                self.logger.info('Rebooting device to ADB mode...')
                self.reboot_to('adb')
                self.wait_for('adb', timeout=160)
                self.logger.done()
                    
    def clearLogs(self):
        """ clear logs """
        def checkStatus(text):
            _text = re.sub('[\t\r\n]+', ' ', text)
            if 'no such file' in _text.lower() or _text.strip() == '':
                self.logger.done()
            else:
                self.logger.error('Logs were not deleleted: {}'.format(text), self.syslogger)

        mode = self.get_mode()
        try:
            if mode == 'fastboot':
                self.logger.info('Rebooting device to ADB mode...')
                self.reboot_to('adb')
            self.wait_idle()
            self.root()
            # dontpanic
            self.logger.info('Clearing /data/dontpanic...')
            checkStatus(self.shell('rm -r /data/dontpanic/*', errors=False, empty=True))
            checkStatus(self.shell('rm -r /data/vendor/dontpanic/*', errors=False, empty=True))
            # aplogd
            self.logger.info('Clearing /data/aplogd...')
            checkStatus(self.shell('rm -r /data/aplogd/*.gz', errors=False, empty=True))
            checkStatus(self.shell('rm -r /data/vendor/aplogd/*.gz', errors=False, empty=True))
            # pstore
            self.logger.info('Clearing /sys/fs/pstore...')
            checkStatus(self.shell('rm -r /sys/fs/pstore/*', errors=False, empty=True))
        except ResultError as e:
            self.syslogger.exception(e)
            raise
        finally:
            if mode != 'adb':
                self.logger.info('Rebooting device to {} mode...'.format(mode.upper()))
                self.reboot_to(mode)
                self.wait_for(mode, timeout=160)
                self.logger.done()
