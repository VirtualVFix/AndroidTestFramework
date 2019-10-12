# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 29, 2015 12:04:19 PM$"

import re
from .base import Base
from config import CONFIG
from time import time, sleep
from libs.core.logger import getLogger


class Temperature(Base):
    def __init__(self, serial, logger=None):
        super(Temperature, self).__init__(serial, logger=logger or getLogger(__file__))
        self._thermal_sensors = None
        self._run_temperature = CONFIG.propertyByDevice('DEVICE', 'RUN_TEMPERATURE')
        
    def getValue(self, text):
        match = re.search('.*?(result[\s:]*|sensor|ts)*([\d]+).*', text, re.IGNORECASE|re.DOTALL)
        if match: 
            return int(match.group(2))
        return -1   
        
    def prepare(self):
        data = CONFIG.propertyByPlatform('DEVICE', 'THERMAL_SENSOR')
        if data is None: return
        
        _str = [x for x in data if isinstance(x, str) and x.strip() != '' and '/' in x]
        _val = [x for x in data if isinstance(x, int) or (isinstance(x, str) and '/' not in x)]
        
        # check string parameters
        for x in _str:
            try: 
                raw = self.sh('cat ' + x).replace('\r','').replace('\n','')
                self.syslogger.info('{} | RAW: {}'.format(x, raw))
                temp = self.getValue(raw)
                if temp > 0: 
                    self._thermal_sensors.append(x)
                    self.syslogger.info('ADDED SENSOR: {} | temp: {}'.format(x,temp))
            except Exception as e:
                self.syslogger.error(e)
            
        # check int parameters
        if len(_val) != 0:
            out = (x.strip() for x in self.sh('ls /sys/class/thermal/').replace('\r','').replace('\n',' ').split(' ')
                   if x.strip() != '')
            for x in out:
                try:
                    raw_type = self.sh('cat /sys/class/thermal/' + x + '/type').replace('\r','').replace('\n','')
                    raw_temp = self.sh('cat /sys/class/thermal/' + x + '/temp').replace('\r','').replace('\n','')
                    self.syslogger.info('/sys/class/thermal/{} | RAW type: {} | RAW temp: {}'
                                        .format(x,raw_type,raw_temp))
                    val = self.getValue(raw_type)
                    temp = self.getValue(raw_temp)
                    if (temp > 0 and int(val) in _val) or (raw_type in _val): 
                        self._thermal_sensors.append('/sys/class/thermal/' + x + '/temp')
                        self.syslogger.info('ADDED SENSOR: '
                                            + '/sys/class/thermal/{} | raw type: {} | int type: {} | temp: {}'
                                            .format(x, raw_type, val, temp))
                except Exception as e:
                    self.syslogger.error(e)

        self.syslogger.info('Temperature control temperature: {}'.format(self._run_temperature))
        self.syslogger.info('Temperature control sensors: {}'.format(self._thermal_sensors))

    def temperatureControl(self):
        if CONFIG.DEVICE.ENABLE_TEMPERATURE_CONTROL:
            # find required thermal sensors
            if self._thermal_sensors is None: 
                self._thermal_sensors = []
                self.prepare()
            # check sensors
            if len(self._thermal_sensors) != 0:
                def getMaxTemp():
                    temp = [float(x)/10**(len(str(x))-2) for x in (self.getValue(self.sh('cat ' + x))
                                                                   for x in self._thermal_sensors)]
                    self.syslogger.info('Temperature levels: {}'.format(temp))
                    return max(temp)
                _state = CONFIG.TEST.CURRENT_STATE
                try:
                    _temp = getMaxTemp()
                    self.logger.info('Current temperature: {}C'.format(_temp))
                    if _temp > self._run_temperature:
                        CONFIG.TEST.CURRENT_STATE = 'Wait for cooling'
                        self.sh('input keyevent 26') # turn off screen
                        t = time()
                        _show = True
                        while True:
                            if _show: 
                                self.logger.info('Current temperature: {}C. Wait for cooling to {}C ...'
                                                 .format(_temp, self._run_temperature))
                                _show = False                            
                            self.syslogger.info('Current temperature: {}C. Wait for cooling to {}C ...'
                                                .format(_temp, self._run_temperature))
                            sleep(1)                
                            _temp = getMaxTemp()
                            # cold enough
                            if _temp <= self._run_temperature: 
                                self.logger.info('Current temperature: {}C. Cooling time: {} sec.'
                                                 .format(_temp, int(time()-t)))
                                self.syslogger.info('Current temperature: {}C. Cooling time: {} sec.'
                                                    .format(_temp, int(time()-t)))
                                break
                            # timeout expired
                            if CONFIG.DEVICE.COOLING_TIMEOUT > 0 and (time()-t > CONFIG.DEVICE.COOLING_TIMEOUT):
                                CONFIG.TEST.CURRENT_STATE = _state
                                self.logger.newline(self.syslogger)
                                self.logger.warnlist('COOLLING TIMEOUT EXPIRED ! '
                                                     + 'Current temperature: {}C. Cooling time: {} sec.'
                                                     .format(_temp, int(time()-t)), self.syslogger)
                                self.logger.newline(self.syslogger)
                                break
                except Exception as e:
                    self.syslogger.exception(e)
                    CONFIG.TEST.CURRENT_STATE = _state
                    self.logger.warnlist('Temperature control error: {}'.format(e))
                    if CONFIG.SYSTEM.DEBUG:
                        self.logger.exception(e)
                finally:
                    CONFIG.TEST.CURRENT_STATE = _state
            else: 
                self.logger.info('Thermal sensor is N/A. Sleeping {} sec...'
                                 .format(CONFIG.DEVICE.SLEEP_TIME_WITHOUT_SENSOR))
                sleep(CONFIG.DEVICE.SLEEP_TIME_WITHOUT_SENSOR)
