# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 7, 2014 10:04:01 PM$"

import os
from config import CONFIG
from libs.results import XLSResult
from libs.core.logger import getLogger
from libs.results.base import constants as xlsconfing
from libs.device.ui import Wireless, Media, Display, Wizard
from tests.exceptions import TestPrepareError, ResultCollectionError
from .base.constants import USE_POINT_AS_DECIMAL_SYMBOL, BENCHMARKS_DATA
from tests.benchmarks.tools.base.constants import COUNT_RETRIES, AUTO_UNINSTALL_APP
from libs.device.shell import Temperature, Battery, PowerUpReason, PowerUpReasonError, Dmesg, Logcat, Mods


class Benchmarks(Wizard, Wireless, Display, Media, PowerUpReason, Temperature, Battery, Dmesg, Logcat, Mods):
    """ Benchmarks tests implementation """

    def __init__(self, serial, device_prepare=False, skip_wizard=False):
        super(Benchmarks, self).__init__(serial, logger=getLogger(__file__))
        self.device_prepare = device_prepare  # on/off device prepare
        self.skip_wizard = skip_wizard
        self.setUp()
        
    def setUp(self):
        # disable security package_verifier
        self.reboot_to('adb')
        self.wait_idle()
        self.root()
        self.sh("settings put global package_verifier_enable 0", errors=False, empty=True)
        # prepare device
        if not self.device_prepare:
            self.logger.newline()
            self.logger.warning('Initial conditions of device should be:')
            self.logger.warning('1. Display timeout is set to 30 min or Stay awake is ON')
            self.logger.warning('2. WiFi is connected to point')
            self.logger.warning('3. Airplane mode is ON')
            self.logger.warning('4. Location services all DISABLED')
            self.logger.warning('5. [optional] Media volume is mute')
            self.logger.warning('6. [optional] SD card is NOT mounted as internal primary')
            self.logger.newline()
        else:
            self.logger.newline()
            self.logger.info('Preparing device:')
            # if self.skip_wizard:
            #     self.skipSetupWizard()
            # self.setMaxDisplayTimeout()
            # self.muteMediaVolume()
            self.enableAirplaneMode()
            self.logger.newline()
        
        # Build Type info ------------------------------------------------------
        self.logger.info('Device Info: {} [{} ({})][{}_{}_{}]'.format(CONFIG.DEVICE.CPU_HW.upper(),
                                                                      CONFIG.DEVICE.DEVICE_NAME,
                                                                      'x64' if CONFIG.DEVICE.CPU_64_BIT else 'x32',
                                                                      CONFIG.DEVICE.BUILD_RELEASE.upper(),
                                                                      CONFIG.DEVICE.BUILD_TYPE.upper(),
                                                                      CONFIG.DEVICE.BUILD_VERSION))
        if 'userdebug' in CONFIG.DEVICE.BUILD_TYPE:
            self.logger.newline()
            self.logger.warnlist('You using USERDEBUG build for perfomance testing !', self.syslogger)
            self.logger.newline()
        # ----------------------------------------------------------------------
    
        # Creating Results spreadsheet -----------------------------------------
        xlsconfing.USE_POINT_AS_DECIMAL_SYMBOL = USE_POINT_AS_DECIMAL_SYMBOL
        self.bench_results = XLSResult('Benchmarks', os.path.join(CONFIG.SYSTEM.LOG_PATH, "!Benchmarks_{}_{}_{}.xls"
                                       .format(CONFIG.TEST.CURRENT_SUITE, CONFIG.TEST.CURRENT_CASE_INDEX,
                                               CONFIG.TEST.CURRENT_CYCLE)))
        # ----------------------------------------------------------------------
        # Check WiFi connection ------------------------------------------------
        CONFIG.TEST.__iswifienabled__ = self.isWiFiEnabled()
        # connect to point if wifi enabled
        if CONFIG.TEST.__iswifienabled__:
            self.enableWiFiAndPing()
        # ----------------------------------------------------------------------
        # Prepare Mods if available --------------------------------------------
        self.modsPrepare()
        # ----------------------------------------------------------------------
     
    # main launch function
    def launch(self, benchmark_name, cycles = 1, retries = COUNT_RETRIES):
        """ launch benchmark """
        res, msg = False, 'Not run'
        bmark = None
        CONFIG.TEST.TEST_NAME = benchmark_name  # save benchmark name
        CONFIG.TEST.TOTAL_CYCLES = cycles
        try:
            bmark, bdata = self.getBenchmark(benchmark_name)
            self.logger = bmark.logger
            # add new test to results doc
            self.bench_results.new_test(bdata['name'])
            bmark.install()
            for i in range(cycles):  # main cycle
                self.logger.newline()
                self.logger.info("Iteration: {}/{}".format(i+1, cycles))
                bmark.run_index = i  # run index using in screenshots save
                # add ne cycle to results doc
                if i > 0 and i != cycles: 
                    self.bench_results.new_cycle()
                j = 0
                # retries
                while j < retries:
                    j += 1
                    try:
                        self.modsToggle(connect=False, verbose=False) # disable mods if available
                        self.checkDmesg(False)  # find old BCL and LMH triggers
                        self.temperatureControl()  # temperature control
                        self.batteryControl()  # battery control
                        self.powerUpReason()  # check PowerUpReason
                        self.logcatClear()  # clear logcat
                        self.modsToggle(connect=True)  # enable mods if available
                        # start benchmark
                        if benchmark_name.lower() == 'kraken': 
                            self.logger.warning('Release The Kraken !')
                        # running benchmark
                        if benchmark_name.lower() == 'kraken':
                            self.logger.warning('The Kraken is coming !')
                        else:
                            self.logger.info('Starting benchmark...')
                        bmark.start()  # running benchmark
                        self.checkDmesg()  # check BCL and LMH features
                        self.logcatCollection()  # logcat collection
                        self.collectResults(bmark)
                        res, msg = True, ''
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        error = 'Cycle {}/{} [{}] benchmark error: {}'.format(i+1, cycles, benchmark_name, e)
                        self.syslogger.exception(error)
                        if CONFIG.SYSTEM.DEBUG:
                            self.logger.exception(error)
                        else:
                            self.logger.error(error)
                        res, msg = False, str(e)
                        # retry if it's not PowerUpReasonError
                        if j < retries and not isinstance(e, PowerUpReasonError):
                            self.logger.newline()
                            self.logger.warning('Restart attempt {}/{}'.format(j+1, retries))
                            continue
                        raise
                    else:
                        break
                    finally:
                        if bmark is not None: 
                            bmark.stop()
                        self.modsToggle(connect=False)  # disable mods after test if available
                CONFIG.TEST.CURRENT_CYCLE = i+1
        except KeyboardInterrupt:
            raise
        except Exception as e:
            res, msg = False, str(e)
            self.syslogger.exception('Launch [{}] benchmark error: {}'.format(benchmark_name, e))
            self.logger.info('Testing was interrupted. Cycles: {}/{}'.format(CONFIG.TEST.CURRENT_CYCLE,
                                                                             CONFIG.TEST.TOTAL_CYCLES))
            if CONFIG.SYSTEM.DEBUG:
                self.logger.exception('Launch [{}] benchmark error: {}'.format(benchmark_name, e))
            else:
                self.logger.error('Launch [{}] benchmark error: {}'.format(benchmark_name, e))
            # add fail message to results doc
            try:self.bench_results.failed_test('FAILED', str(e))
            except:pass
            self.powerUpReason()
        else:
            self.logger.info('Testing has been completed. Cycles: {}/{}'.format(CONFIG.TEST.CURRENT_CYCLE,
                                                                                CONFIG.TEST.TOTAL_CYCLES))
        finally:
            if bmark is not None:
                # return default logger
                self.logger = getLogger(__file__)
                try:
                    # try to collect results if error is observed
                    if not res:
                        self.collectResults(bmark)
                except Exception as e:
                    self.syslogger.exception(e)
                finally:
                    if AUTO_UNINSTALL_APP:
                        bmark.uninstall()
        return res, msg
    
    def checkDmesg(self, verbose=True):
        res = self.dmesg(['bcl', 'lmh'])
        if res is not None and verbose:
            self.logger.newline(self.syslogger)
            for x in res:
                self.logger.warnlist('%s triggered: %s. | Test: %s | Suite: %s | Statename: %s | Cycle: %s' \
                                      % (x[2].upper(), x[0] + x[1],  CONFIG.TEST.CURRENT_TEST,
                                         CONFIG.TEST.CURRENT_SUITE, CONFIG.TEST.CURRENT_STATE,
                                         CONFIG.TEST.CURRENT_CYCLE), self.syslogger)
            self.logger.newline(self.syslogger)

    def getBenchmark(self, benchmark_name):
        """
        Get benchmark class object by name

        Args:
             benchmark_name (str): Benchmark name to load test settings from BENCHMARKS_DATA dict

        Returns:
            tuple: (benchmark class implementation, benchmark settings dict)
        """
        if benchmark_name not in BENCHMARKS_DATA:
            raise TestPrepareError('Benchmarks [%s] not found in config file !' % benchmark_name)

        bdata = BENCHMARKS_DATA[benchmark_name]
        try:
            if '@' in bdata:
                if bdata['@'] not in BENCHMARKS_DATA:
                    raise TestPrepareError('Linked benchmark "{}" does not exists !'.format(bdata['@']))
                else:
                    for x in BENCHMARKS_DATA[bdata['@']]:
                        if x not in bdata:
                            bdata[x] = BENCHMARKS_DATA[bdata['@']][x]
            # loading module
            from libs.core.tools import load_module
            _path = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'bench'),
                                 '%s.py' % bdata['class'])
            mod = load_module('benchmark_%s' % benchmark_name, _path)
            # get benchmark class
            cls = getattr(mod, bdata['class'], None)
            if cls is None:
                raise TestPrepareError('Benchmark implementation not found !')
            return cls(attributes=bdata, serial=self.serial), bdata
        except Exception as e:
            self.syslogger.exception(e)
            raise TestPrepareError('Error of loading [%s] benchmark class: %s' % (bdata["class"], e))
        
    def collectResults(self, benchmark_obj):
        try:
            benchmark_obj.logger.info("Saving results...")
            benchmark_obj.collect_results(self.bench_results)
            self.bench_results.collect_results(
                summary_type=benchmark_obj.attributes['results_summary']
                if 'results_summary' in benchmark_obj.attributes else 'best_and_average'
                if 'average_list' in benchmark_obj.attributes else 'best',
                average_list = benchmark_obj.attributes['average_list']
                if 'average_list' in benchmark_obj.attributes else None,
                order_list = benchmark_obj.attributes['order']
                if 'order' in benchmark_obj.attributes else None)
            benchmark_obj.logger.info('Done.')
        except Exception as e:
            raise ResultCollectionError('Collect results error: {}'.format(e))
        
    def uninstallJunitRunner(self):
        """ uninstall JUnitRunner after all tests """
        from libs.device.ui import JUnitRunner
        junit = JUnitRunner(self.serial)
        junit.logger = self.logger
        junit.uninstallJUnitTestsLauncher()
