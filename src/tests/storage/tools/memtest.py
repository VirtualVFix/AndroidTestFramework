# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Feb 13, 2017 14:12:00 PM$"

import os
import re
from time import sleep
from config import CONFIG
from libs.core.logger import getLogger
from tests.exceptions import ResultsNotFoundError, ResultCollectionError
from .base.constants import FS_PERFORMANCE_MEASURE_UNITS, MEMTEST_FILED_COUNT
from libs.device.shell import Temperature, Battery, PowerUpReason, Mods, Display
from .base.constants import APKS_DIR, MEMTEST_UTIL64, MEMTEST_UTIL32, INSTALL_PATH, MEMTEST_NAME


class Memtest(PowerUpReason, Temperature, Battery, Mods, Display):
    def __init__(self, serial, xls_results):
        super(Memtest, self).__init__(serial, logger=getLogger(__file__))
        self.xls_results = xls_results
        self.run_path = ''
        self.__prepare()
        
    def __prepare(self):
        self.reboot_to('adb', force=False, timeout=120, verbose=True)
        self.wait_for('adb', timeout=300, verbose=True)
        # Prepare Mods if available --------------------------------------------
        self.modsPrepare()
        # ----------------------------------------------------------------------
        
        try: # check memtest utility 
            self.sh('memtest', errors=True, empty=False)
            self.logger.info('memtest util is integrated to build !')
        except Exception as e:
            self.syslogger.error(e)
            self.logger.info('Installing memtest util...')
            self.push(os.path.join(APKS_DIR, (MEMTEST_UTIL64 if CONFIG.DEVICE.CPU_64_BIT else MEMTEST_UTIL32)),
                                   INSTALL_PATH + MEMTEST_NAME)
            self.sh('chmod 755 ' + INSTALL_PATH + 'memtest')
            # self.logger.done()
            self.run_path = INSTALL_PATH
    
    def __collect_results(self, out, measure_units='MB'):
        try:
            self.logger.info('Collecting results...')
            results = re.findall('\s([\w\d/]+):\s([\d.]+)\s([\w]+)/', out)

            if len(results) != MEMTEST_FILED_COUNT:
                raise ResultsNotFoundError('Test results are not full ! Required "{}" fields, found: "{}"'
                                           .format(MEMTEST_FILED_COUNT, len(results)))

            # add results for spreadsheet
            for name,val,unit in results:
                if unit.upper() not in FS_PERFORMANCE_MEASURE_UNITS:
                    raise ResultCollectionError('Inconsistent measure unit in test results. '
                                                + 'Required units: "{}", found: "{}".'
                                                .format(','.join(FS_PERFORMANCE_MEASURE_UNITS), unit.upper()))
                self.xls_results.add_name(name)
                _tm = float(val)
                # convert value to required units
                if unit.upper() != measure_units:
                    _ind_reqired = FS_PERFORMANCE_MEASURE_UNITS.index(measure_units)
                    _ind_current = FS_PERFORMANCE_MEASURE_UNITS.index(unit.upper())
                    if _ind_reqired < _ind_current:
                        for i in range(_ind_current-_ind_reqired):
                            _tm *= 1024
                    else:
                        for i in range(_ind_reqired-_ind_current):
                            _tm /= 1024
                    self.logger.warning('"{}" units for "{}" field was converted to "{}".'.format(unit.upper(),
                                                                                                  name, measure_units))
                self.xls_results.add_result(_tm)
        except Exception as e:
            try:self.xls_results.failed_test('FAILED', str(e))
            except:pass
            raise
        finally:
            self.xls_results.collect_results()
            
    def launch(self, params='copy_bandwidth', cycles=1, delay=120, timeout=900, measure_units='MB'):
        CONFIG.TEST.TEST_NAME = 'memtest' # save benchmark name
        CONFIG.TEST.TOTAL_CYCLE = cycles
        try:
            # add new test
            self.xls_results.new_test("memtest", style=self.xls_results.style_bold)

            self.reboot_to('adb', force=True, timeout=600, verbose=True)
            self.wait_idle(timeout=600, verbose=True)
            
            if delay > 0:
                self.turnScreenOff(verbose=True)
                self.logger.info('Sleeping %s seconds due to launch delay...' % delay)
                sleep(delay)
                
            # test cycle
            current_cycle = 0
            while current_cycle < cycles:
                # device control
                self.batteryControl() # battery control
                self.temperatureControl() # temperature control 
                self.powerUpReason() # check PowerUpReason
                self.modsToggle(connect=True) # enable mods if available
               
                self.logger.info('Starting memtest with "{}" parameter. Cycle: {}/{}'.format(params, current_cycle+1,
                                                                                             cycles))
                # add new cycle 
                if current_cycle > 0 and current_cycle != cycles: 
                    self.xls_results.new_cycle()
                # launch spript
                self.logger.info('Waiting for memtest results...')
                out = self.sh(self.run_path + MEMTEST_NAME + ' ' + params, errors=True, empty=False, timeout=timeout)
                self.syslogger.info(out)
                self.__collect_results(out, measure_units)
                
                current_cycle += 1
                CONFIG.TEST.CURRENT_CYCLE = current_cycle
            res, msg = True, ''
        except Exception as e:
            self.syslogger.exception(e)
            self.logger.info('Testing was interrupted. Cycles: {}/{}'.format(CONFIG.TEST.CURRENT_CYCLE,
                                                                             CONFIG.TEST.TOTAL_CYCLES))
            if CONFIG.SYSTEM.DEBUG:
                self.logger.exception(e)
            res, msg = False, str(e)
        else:
            self.logger.info('Testing has been completed. Cycles: {}/{}'.format(CONFIG.TEST.CURRENT_CYCLE,
                                                                                CONFIG.TEST.TOTAL_CYCLES))
        finally: 
            self.modsToggle(connect=False) # disable mods after test if available
        return res, msg
