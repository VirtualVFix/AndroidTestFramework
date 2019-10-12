# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Dec 10, 2014 1:09:26 PM$"

import os
import re
import xlrd
import platform
from time import sleep
from config import CONFIG
from libs.results import XLSResult
from .base.constants import APKS_DIR
from libs.core.logger import getLogger
from libs.device.shell import Temperature, Battery, PowerUpReason, Mods, SDCard, Display
from tests.exceptions import ResultsNotFoundError, TestExecutionError, TestPrepareError


class Iozone(PowerUpReason, Temperature, Battery, Mods, SDCard, Display):
    def __init__(self, serial, run_path, scriptname='iozone_test.sh', results_order_list=None):
        super(Iozone, self).__init__(serial, logger=getLogger(__file__))
        self.serial = serial
        self.run_path = run_path
        self.scriptname = scriptname

        self.iozone_results = XLSResult('Iozone', os.path.join(CONFIG.SYSTEM.LOG_PATH,
                                                               "!Iozone_%s_%s_%s.xls" % (CONFIG.TEST.CURRENT_SUITE,
                                                                                         CONFIG.TEST.CURRENT_CASE_INDEX,
                                                                                         CONFIG.TEST.CURRENT_CYCLE)))
        self.order_list = results_order_list or []
        self.__isIozoneStarted = False
        self.__errorList = []
        self.__prepare()

    def __prepare(self):
        self.reboot_to('adb', timeout=120)
        self.wait_for('adb', timeout=300, verbose=True)
        self.root()
        self.iozone_results.new_test("CPU " + self.sh('cat /proc/cpuinfo | grep Revision').split('\n')[0],
                                     style=self.iozone_results.style_bold)
        try:
            # sdcard name
            self.iozone_results.new_test(
                "SD card name: [" + self.sh('cat /sys/block/mmcblk1/device/name', errors=False,
                                            remove_line_symbols=True) + ']', style=self.iozone_results.style_bold)
            # sdcard serial
            self.iozone_results.new_test(
                "SD card serial: [" + self.sh('cat /sys/block/mmcblk1/device/serial', errors=False,
                                              remove_line_symbols=True) + ']', style=self.iozone_results.style_bold)
            # sdcard class
            self.iozone_results.new_test(
                "SD card class: [" + self.sh('cat /sys/block/mmcblk1/device/speed_class', errors=False,
                                             remove_line_symbols=True) + ']', style=self.iozone_results.style_bold)
            # sdcard speed
            self.iozone_results.new_test(
                "SD card speed: [" + self.sh('cat /sys/block/mmcblk1/device/uhs_speed_grade', errors=False,
                                             remove_line_symbols=True)+ ']', style=self.iozone_results.style_bold)
#            sdcard = "SD Card info: Name[" + self.sh('cat /sys/block/mmcblk1/device/name').replace('\r\r\n\n', '')
#            sdcard += "], SN[" + self.sh('cat /sys/block/mmcblk1/device/serial').replace('\r\r\n\n', '')
#            sdcard += "], class[" + self.sh('cat /sys/block/mmcblk1/device/speed_class').replace('\r\r\n\n', '')
#            sdcard += "], speed[" + self.sh('cat /sys/block/mmcblk1/device/uhs_speed_grade').replace('\r\r\n\n', '') + "]"
#            self.iozone_results.new_test(sdcard, style=self.iozone_results.style_bold)
        except Exception as e:
            self.logger.error(e)
            self.syslogger.exception(e)

        # Prepare Mods if available --------------------------------------------
        self.modsPrepare()
        # ----------------------------------------------------------------------

        # clear previous run on /data if available
        try:self.sh('rm /data/iozone_test*')
        except: pass

        self.logger.info('Installing utils...')
        self.push(os.path.join(APKS_DIR, self.scriptname), self.run_path)
        self.sh('chmod 755 ' + self.run_path + self.scriptname)
        self.push(os.path.join(APKS_DIR, ('mot.iozone-64' if CONFIG.DEVICE.CPU_64_BIT else 'mot.iozone-32')),
                  self.run_path + 'iozone')
        self.sh('chmod 755 ' + self.run_path + 'iozone')
        # self.logger.done()
        self.logger.info('Test script: "{}"'.format(self.scriptname), self.syslogger)

    def __collect_results(self, filelist):
        try:
            # rename field according to google spreadsheet
            def renameFields(field):
                if field is None:
                    return None
                _field = field.lower().strip()
                if 'random' not in _field:
                    if 're-' in _field or 'rewrite' in _field or 'reread' in _field:
                        if 'write' in _field:
                            return re.sub('rewrite|re-write','re-writer report', _field)
                        else: return re.sub('reread|re-read','re-reader report', _field)
                    else:
                        return _field.replace('initial','') \
                                     .replace('read','reader report') \
                                     .replace('write','writer report')
                return _field

            self.logger.info('Collecting results...')
            res = [] # sorting resutls
            for x in self.order_list:
                grp = []
                for y in x:
                    for k in filelist:
                        if y in k: grp.append(k)
                res.append(grp)

            # find results folder
            results_directory = CONFIG.SYSTEM.LOG_PATH
            for direcrory,s,files in os.walk(CONFIG.SYSTEM.LOG_PATH):
                for f in files:
                    if f in filelist:
                        results_directory = (direcrory+os.sep) if not direcrory.endswith(os.sep) else direcrory
                        break

            # collect results
            for grp in res:
                name = [None for _ in range(len(grp)*2+2)]
                val = [None for _ in range(len(grp)*2+2)]
                for i in range(len(grp)):
                    self.logger.info('{}...'.format(grp[i]))
                    book = xlrd.open_workbook(results_directory + grp[i], encoding_override="utf-8")
                    sheet = book.sheet_by_index(0)
                    if re.search('_s[\d]+', grp[i], re.IGNORECASE):  # single thread results
                        if i == 0:
                            name[i] = sheet.cell(3,0).value
                            name[i+1+len(grp)] = sheet.cell(6,0).value
                            val[i] = None
                            val[i+1+len(grp)] = None
                        elif name[0] != sheet.cell(3,0).value:
                            raise ResultsNotFoundError('Results "{}" cannot be grouped !'.format(grp))
                        name[i+1] = str(int(sheet.cell(4,1).value))
                        name[i+2+len(grp)] = str(int(sheet.cell(7,1).value))
                        val[i+1] = sheet.cell(5,1).value
                        val[i+2+len(grp)] = sheet.cell(8,1).value
                    else: # multi thread results
                        _size = re.search('([\d]+)', sheet.cell(2,0).value).group(1)
                        _offset = 2 if '_w' in grp[i] else 0
                        if i == 0:
                            name[i] = sheet.cell(6-_offset,0).value + '(M)'
                            name[i+1+len(grp)] = sheet.cell(7-_offset,0).value + '(M)'
                            val[i] = None
                            val[i+1+len(grp)] = None
                        elif name[0] != sheet.cell(6-_offset,0).value+'(M)':
                            raise TestExecutionError('Results "{}" cannot be grouped !'.format(grp))
                        name[i+1] = _size
                        name[i+2+len(grp)] = _size
                        val[i+1] = sheet.cell(6-_offset,2).value
                        val[i+2+len(grp)] = sheet.cell(7-_offset,2).value

                # add results for spreadsheet
                for i in range(len(name)):
                    self.iozone_results.add_name(renameFields(name[i]))
                    self.iozone_results.add_result(val[i])

            self.logger.info('Done.')
        except Exception as e:
            self.syslogger.exception(e)
            if CONFIG.SYSTEM.DEBUG:
                self.logger.exception(e)
            try:self.iozone_results.failed_test('FAILED', str(e))
            except:pass
            raise
        finally:
            self.iozone_results.collect_results()

    def _getRamSize(self):
        """ get ram size and convert it to Gigabytes """
        ram = -1
        try:
            ram = self.sh('cat /sys/ram/info')
            match = re.search('([\d]+)([MG])', ram, re.I)
            size = ''
            if match:
                ram = match.group(1)
                size = match.group(2).lower()
            if size == 'm':
                ram = float(ram)/1000
            elif size == 'g':
                ram = float(ram)
            else: raise TestPrepareError('Ram cannot be got from "/sys/ram/info": Not supported format !')
        except Exception as e:
            self.syslogger.exception(e)
            if CONFIG.SYSTEM.DEBUG:
                self.logger.error(e)
        return ram

    def _getPartitionSize(self, partition):
        thread_size = -1
        try:
            size = self.sh('df {}'.format(partition)).replace('\r','')
            line = [x.strip() for x in size.split('\n') if x.strip() != ''][1]
            size = [x for x in line.split(' ') if x != ''][3]
            if 'k' in size.lower():
                return float(size[:-1])/1024/1024
            elif 'm' in size.lower():
                return float(size[:-1])/1024
            elif 'g' in size.lower(): return float(size[:-1])
            else: return float(size)/1024/1024
        except Exception as e:
            self.syslogger.exception(e)
            if CONFIG.SYSTEM.DEBUG:
                self.logger.error(e)
        return thread_size

    def isSpaceNotEnoughForTest(self, partition, threads=4):
        """ return True if free space on partition less then ram * threads (4 for default) """
        ram = self._getRamSize()
        size = self._getPartitionSize(partition)
        self.syslogger.info('RAM SIZE: {}Gb | STORAGE SIZE: {}Gb'.format(ram, size))
        try:
            if ram == -1 or size == -1:
                raise TestPrepareError('Partition or Ram size cannot no be got !')
            if ram*threads >= size:
                return True
        except Exception as e:
            self.syslogger.exception(e)
            if CONFIG.SYSTEM.DEBUG:
                self.logger.error(e)
        return False
            
    def runScript(self, command, timeout, verbose=False):
        """ launch scrip via Command class directly with check spesific errors in realtime """
        logger = self.logger
        self.__isIozoneStarted = False
        self.__errorList = []
        __errorLineCount = 3
        
        def checkLineErrors(line):
            """ check errors in real time """
            if verbose:
                logger.info(line)
            _line = line.lower() if line is not None else ''
            if 'command line used' in _line:
                self.__isIozoneStarted = True
            if 'report is in' in _line: 
                logger.info('Iozone test is completed')
            if 'can not open temp file: iozone.tmp' in _line or 'error' in _line or 'no space left on device' in _line \
                    or 'read-only file system' in _line or 'not file' in _line: 
                if self.__isIozoneStarted:
                    tm = re.sub('[\t\r\n]+', '', line.strip())
                    if tm != '': 
                        self.__errorList.append(tm)
                else: logger.warn('Prepare error: ' + line)
            if len(self.__errorList) > 0: 
                logger.error(line)
            if len(self.__errorList) >= __errorLineCount:
                raise TestExecutionError('Iozone execution error: {}'.format('; '.join(self.__errorList)))

        return self.sh(command, timeout=timeout, interactive_filter=checkLineErrors)

    def launch(self, partition, platform=None, thread_size=None, cycles=1, delay=60, timeout=900, verbose=False,
               sdcard=False):
        CONFIG.TEST.TEST_NAME = 'Iozone on ' + partition  # save benchmark name
        CONFIG.TEST.TOTAL_CYCLE = cycles
        try:
            # add new test
            _partition = '/'.join(partition.split('/')[:3])
            self.iozone_results.new_test(_partition, style=self.iozone_results.style_bold)
            current_cycle = 0
            while current_cycle < cycles:
                self.reboot_to('adb', force=True, timeout=600, verbose=True)
                self.wait_idle(timeout=600, verbose=True)
                self.root(verbose=True)
                
                # get SDCard path if required
                if sdcard is True:
                    partition = self.detectSDCard(partition)
                    if partition is None:
                        raise TestPrepareError('SD card is N/A !')

                # device control
                self.batteryControl()  # battery control
                if delay > 0:
                    self.turnScreenOff(verbose=True)
                    self.logger.info('Sleeping %s seconds due to launch delay...' % delay)
                    sleep(delay)
                self.temperatureControl()  # temperature control
                self.powerUpReason()  # check PowerUpReason
                self.modsToggle(connect=True) # enable mods if available

                # clear data
                if '/storage/emulated' in partition:
                    self.sh('rm /storage/emulated/0/iozone_test*', errors=False)
                self.sh('rm {}/iozone_test*'.format(partition), errors=False)
                
                # check if thread size option is required
                _ms = (' -ms ' + str(thread_size)) if thread_size is not None else ''
                if _ms == '' and self.isSpaceNotEnoughForTest(partition): 
                    _ms = ' -ms 1'
                    self.logger.warn('Not enough space on device for test with default thread size. '
                                     + 'Thread size will be configureg to 1Gb !', self.syslogger)
                params = '' + ((' -T ' + platform) if not platform is None else '') + _ms
                self.logger.info('Starting iozone on "{}" partition{}. Cycle: {}/{}'
                                 .format(partition, (' with parameters:"' + params + '"') if params != '' else '' ,
                                         current_cycle+1, cycles))
                # add new cycle 
                if current_cycle > 0 and current_cycle != cycles: self.iozone_results.new_cycle()
                
                # launch spript
                self.logger.info('Waiting for Iozone results...')
                out = self.runScript(self.run_path + self.scriptname + ' -c -d ' + partition + params, timeout, verbose)
                # self.syslogger.info(out)

                # search result folder in output
                match = re.search('report is in (.*)($|[\r\t\n]+)', out, re.I)
                if not match: 
                    raise ResultsNotFoundError('Results are not found !')
                res = match.group(1)
                self.logger.info('Results path: ' + res)
                
                xls = self.sh('ls ' + res, errors=True, empty=False)
                xls = [x.strip().replace('\r', '') for x in xls.split('\n') if x != '']
                self.logger.info('Pulling results...')
                self.pull(res, CONFIG.SYSTEM.LOG_PATH)

                self.__collect_results(xls)
                
                current_cycle += 1
                CONFIG.TEST.CURRENT_CYCLE = current_cycle
            res, msg = True, ''
        except Exception as e:
            res, msg = False, str(e)
            self.syslogger.exception(e)
            self.logger.info('Testing was interrupted. Cycles: {}/{}'.format(CONFIG.TEST.CURRENT_CYCLE,
                                                                             CONFIG.TEST.TOTAL_CYCLES))
            if CONFIG.SYSTEM.DEBUG:
                self.logger.exception(e)
        else:
            self.logger.info('Testing has been completed. Cycles: {}/{}'.format(CONFIG.TEST.CURRENT_CYCLE,
                                                                                CONFIG.TEST.TOTAL_CYCLES))
        finally:
            self.modsToggle(connect=False) # disable mods after test if available
        return res, msg
