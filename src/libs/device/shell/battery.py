# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Mar 6, 2015 11:11:20 AM$"

import re
from time import time
from time import sleep
from config import CONFIG
from .display import Display
from libs.core.logger import getLogger
from libs.device.shell.base.constants import BATTERY_PERCENTAGE_THESHOLD_WARNING
from libs.device.shell.base.constants import BATTERY_PERCENTAGE_THESHOLD_TIMEOUT
from libs.device.shell.base.constants import BATTERY_STATUS_CHECK_DELAY, DUMPSYS_BATTERY_TEMPERATURE
from libs.device.shell.base.constants import DUMPSYS_BATTERY_VOLTAGE, BATTERY_CHARGING_TIMEOUT, DUMPSYS_BATTERY_CAPACITY


class Battery(Display):
    """ Device battery control system """
    def __init__(self, serial, logger=None):
        super(Battery, self).__init__(serial, logger=logger or getLogger(__file__))

    def __getBatteryStateViaDumpsys(self):
        # get bettery level
        current = int(re.search('level:\s([\d]+)[\r\t\n]+', self.sh(DUMPSYS_BATTERY_CAPACITY), re.I).group(1))
        # get voltage
        try:
            voltage = re.findall('\s+voltage:\s([\d]+)[\r\t\n]+', self.sh(DUMPSYS_BATTERY_VOLTAGE))[-1]
            voltage = float(voltage)/10**(len(voltage)-1)
        except Exception as e:
            self.syslogger.error(e)
            voltage = None

        # get temperature
        try:
            temp = re.search('temperature:\s([\d]+)[\r\t\n]+', self.sh(DUMPSYS_BATTERY_TEMPERATURE), re.I).group(1)
            temp = float(temp)/10**(len(temp)-2)
        except Exception as e:
            self.syslogger.error(e)
            temp = None
        return current, voltage, temp            
    
    def __printBatteryState(self, current, voltage, temperature):
        self.logger.info('Current battery capacity: {}%'.format(current))

        if voltage is not None:
            self.logger.info('Current battery voltage: {}V'.format(voltage))

        if temperature is not None:
            self.logger.info('Current battery temperature: {}C'.format(temperature))

        self.syslogger.info('Current battery capacity: %s%% | voltage: %sV ' % (current, voltage)
                            + '| Test: %s | Suite: %s ' % (CONFIG.TEST.CURRENT_TEST, CONFIG.TEST.CURRENT_SUITE)
                            + '| State name: %s | Cycle: %s' % (CONFIG.TEST.CURRENT_STATE,
                                                                CONFIG.TEST.CURRENT_CYCLE))

    def batteryControl(self, ignore_global_settings=False):
        """ Check battery level and if it less min wait when battery charged to max """
        if CONFIG.DEVICE.BATTERY_CONTROL or ignore_global_settings:
            _state = CONFIG.TEST.CURRENT_STATE
            _charge_mode = False
            try:
                if self.get_mode() == 'fastboot':
                    return              
                
                current, voltage, temperature = self.__getBatteryStateViaDumpsys()
                self.__printBatteryState(current, voltage, temperature)
                
                if current < CONFIG.DEVICE.BATTERY_CONTROL_LEVELS[0]:
                    _charge_mode = True
                    CONFIG.TEST.CURRENT_STATE = 'Battery charging'
                    self.logger.warning('Battery capacity is low. Lower threshold was configured to {}%.'
                                        .format(CONFIG.DEVICE.BATTERY_CONTROL_LEVELS[0]), self.syslogger)
                    self.logger.info('Charging battery to {}% ...'.format(CONFIG.DEVICE.BATTERY_CONTROL_LEVELS[1]),
                                     self.syslogger)
                    try:
                        self.turnScreenOff(verbose=True)
                    except Exception as e:
                        self.syslogger.exception(e)
                        
                    t = time()
                    prev = current
                    while True:
                        # switch switchboard to charging mode 
                        if CONFIG.SWITCH.CLASS is not None:
                            CONFIG.SWITCH.CLASS(CONFIG.SWITCH.SERIAL)\
                                .switch_to_charging_mode(timeout=BATTERY_STATUS_CHECK_DELAY*2)
                            
                        sleep(BATTERY_STATUS_CHECK_DELAY)
                        
                        current, voltage, temperature = self.__getBatteryStateViaDumpsys()
                        if prev < current-BATTERY_PERCENTAGE_THESHOLD_TIMEOUT and time()-t > BATTERY_CHARGING_TIMEOUT:
                            self.syslogger.error('Battery does not charging during {} sec.'.format(int(time()-t)))
                            raise RuntimeError(self.syslogger.lastmessage())
                        if current <= prev+BATTERY_PERCENTAGE_THESHOLD_WARNING and (time()-t > BATTERY_CHARGING_TIMEOUT):

                            CONFIG.TEST.CURRENT_STATE = _state
                            self.logger.newline()
                            self.logger.warnlist('Battery charging rate is very low during %d sec.!' % (int(time()-t)),
                                                 self.syslogger)
                            self.logger.newline()
                        self.__printBatteryState(current, voltage, temperature)
                        if current >= CONFIG.DEVICE.BATTERY_CONTROL_LEVELS[1]:
                            self.logger.info('Battery charging is completed. Charging time: %d sec.' % (int(time()-t)),
                                             self.syslogger)
                            break
                        prev = current
            except Exception as e:
                CONFIG.TEST.CURRENT_STATE = _state
                self.logger.warnlist('Failed to get the battery state: %s' % e, self.syslogger)
            finally: 
                CONFIG.TEST.CURRENT_STATE = _state
                # switch switchboard to normal mode 
                if CONFIG.SWITCH.CLASS not in [None, ''] and _charge_mode is True:
                    CONFIG.SWITCH.CLASS(CONFIG.SWITCH.SERIAL).switch_to_normal_mode()
                
    def checkBattery(self):
        return self.batteryControl()
