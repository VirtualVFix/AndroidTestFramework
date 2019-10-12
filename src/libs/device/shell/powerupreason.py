# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Aug 16, 2013 3:45:47 PM$"

import os
import re
from .base import Base
from libs.core.logger import getLogger
from libs.device.shell.base.exceptions import PowerUpReasonError
from libs.cmd.implement.exceptions import ObjectDoesNotExistError
from libs.device.shell.base.constants import DEVICE_POWER_UP_REASONS, DEVICE_NORMAL_POWER_UP_REASONS


class PowerUpReason(Base):
    def __init__(self, serial, logger=None):
        super(PowerUpReason, self).__init__(serial, logger=logger or getLogger(__file__))
        self.fail_reason = None

    def _checkPowerUpReason(self, cmd):
        try:
            bootinfo_lines = str(self.sh(cmd))
            if not 'no such file' in bootinfo_lines.lower():
                bootinfo_lines = bootinfo_lines.split(os.linesep)
                self.syslogger.info(bootinfo_lines[0])
                match = re.search("POWERUPREASON[:\s]+0x([\d]+)", bootinfo_lines[0], re.I)
                if match and match.group(1) in DEVICE_POWER_UP_REASONS.keys(): 
                    return match.group(1), DEVICE_POWER_UP_REASONS[match.group(1)]
        except ObjectDoesNotExistError as e:
            self.syslogger.info(e)
        return None, None
    
    def getPowerUpReason(self, check_last_kmesg=False):
        code, reason = None, None
        try:
            if self.get_mode() == 'fastboot':
                return 

            self.wait_idle(timeout=900)
            code, reason = self._checkPowerUpReason('cat /proc/bootinfo | grep POWERUPREASON')
            if check_last_kmesg:
                try:
                    if reason == 'SW_AP_RESET': 
                        _code, _reason = self._checkPowerUpReason('cat /data/dontpanic/last_kmsg | grep POWERUPREASON')
                        if _code is not None: 
                            code, reason = _code, _reason
                except Exception as e:
                    self.syslogger.error('Get PowerUpReason from last_kmsg error: {}'.format(e))
            self.syslogger.info('POWERUPREASON: {}/{}'.format(code, reason))
        except Exception as e:
            self.syslogger.exception(e)
        return code, reason   
    
    def checkPowerUpReason(self):
        return self.powerUpReason()
    
    def powerUpReason(self, check_last_kmesg=False):
        """ check powerupreason and get logs if need it """
        try:
            code, reason = self.getPowerUpReason(check_last_kmesg)
            if reason is not None and reason not in DEVICE_NORMAL_POWER_UP_REASONS:
                self.fail_reason = reason
                try:
                    out = self.sh('cat /data/dontpanic/last_kmsg')
                    self.last_kmsg = out if 'not file or' in out.lower() or 'error' in out.lower() else None
                    self.sh('rm /data/dontpanic/last_kmsg')
                except Exception as e:
                    self.syslogger.exception(e)
                raise PowerUpReasonError('Bad powerupreason: 0x{}/{}'.format(code, reason))
        except PowerUpReasonError:
             raise
        except Exception as e:
            self.syslogger.exception(e)
