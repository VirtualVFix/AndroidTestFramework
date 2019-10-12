# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Mar 6, 2015 11:11:20 AM$"

import unittest
from config import CONFIG
from tests.exceptions import TestPrepareError
from tests.storage.tools.iozone import Iozone
from tests.storage.tools.memtest import Memtest
from libs.core.tools import OwnLoop, SkipByDefault


class RegularTestCase(unittest.TestCase):
    """Test suit"""
    # full automate parameters -------------------------------------------------
    auto = False                    # enable full automate mode.
    device = None                   # device name or platform. Spreadsheet will be find by this name. Platform will be detected automatically If == None.
    spreadsheet_id = None           # Spreadsheet ID. It can be specifiy directly.
    sheet_id = ''                   # Identifier of sheet(tab) Goolge in spreadsheet. It can be index, sheet id or sheet name (string). '0' by default.
    sheet_names_column = 'A'        # Identifier of column with test names. Can be columnd name or index.
    sheet_trends_column = 'C'       # Identifier of column with trend formula. Can be columnd name or index.
    sheet_results_column = 'D'      # Identifier of column with values or previous results for compare. Can be columnd name or index.
    sheet_new_column = True         # Save results to new column. Results will be saved to "sheet_values_column" column if false.
    sheet_header_rewrite = False    # Rewrite already exists header data in "sheet_values_column" when "sheet_insert_new_column" == False
    test_cr = None                  # Temperorary variable for add testCR Link to spreadsheet.
    # --------------------------------------------------------------------------
    platform = None                 # Target platform (for example : msm8953).
    verbose = False                 # Print Iozone execution to output in realtime
    thread_size = None              # Indicate the test file size for multithread testing.
    script_name = 'test_v4.7.sh'    # script name from ../apk/ folder
    low_battery_level = 99          # minimal battery level for launch iozone tests
    # data
    data_cycles = 1                 # Test cycles for Iozone test on "/data" partition.
    data_delay = 15*60              # Start delay for Iozone test on "/data" partition.
    data_timeout = 1.5*60*60        # Test timeout Iozone for test on "/data" patition.
    # storage
    storage_cycles = 1              # Test cycles for Iozone test on "/storage/emulated/0/" partition.
    storage_delay = 15*60           # Start delay for Iozone test on "/storage/emulated/0/" partition.
    storage_timeout = 1.5*60*60     # Test timeout for Iozone test on "/storage/emulated/0/" patition.
    # sd card
    sdcard_cycles = 1               # Test cycles for Iozone test on "/data" partition.
    sdcard_delay = 15*60            # Start delay for Iozone test on "/data" partition.
    sdcard_timeout = 7*60*60        # Test timeout for Iozone tests on sdcard.
    # memtest
    memtest_cycles = 10             # Test cycles for memtest.
    memtest_delay = 15*60           # Start delay for memtest.
    memtest_timeout = 20*60         # memtest execution timeout.
    memtest_units = 'MB'            # memtest mesure units

    @classmethod
    def setUpClass(self):
        # iozone
        self.iozone = Iozone(CONFIG.DEVICE.SERIAL, scriptname=self.script_name, run_path='/data/',
                             results_order_list=[['seq_w_m128', 'seq_w_m512'],
                                                 ['seq_r_m128', 'seq_r_m512'],
                                                 ['random_m4']])
        self.memtest = Memtest(CONFIG.DEVICE.SERIAL, self.iozone.iozone_results)

        # set battery level control levels to 100%
        self.battery_levels = CONFIG.DEVICE.BATTERY_CONTROL_LEVELS
        CONFIG.DEVICE.BATTERY_CONTROL_LEVELS = [self.low_battery_level, 99]
        self.iozone.logger.warn('Battery control minimal level is configured to {}%'.format(self.low_battery_level))

        # configure iozone for vertex
        if CONFIG.DEVICE.CPU_HW == '':
            raise TestPrepareError('"ro.board.platform" property is not specified. '
                                   + 'Please use -p "platform=PLATFORM" parameter to specify it manually !')
        self.platform = self.platform.lower() if not self.platform is None else None

        # special parameters for MSM8953
        if 'msm8953' in [CONFIG.DEVICE.CPU_HW, self.platform] and self.thread_size is None:
            self.thread_size = 1

        # full automation mode
        if not self.auto:
            self.automode = None
        else:
            from tests.storage.tools.automode import AutoMode
            self.automode = AutoMode(serial=CONFIG.DEVICE.SERIAL,
                                     spreadsheet_id=self.spreadsheet_id
                                                    or CONFIG.propertyByDevice('TEST', 'STORAGE_AUTO', self.device,
                                                                               'SheetID'),
                                     sheet_identifier=self.sheet_id
                                                      or CONFIG.propertyByDevice('TEST','STORAGE_AUTO', self.device,
                                                                                 'SheetTab') or '0',
                                     client_file_name='atframeworkkey.json')
            self.automode.sheet_names_column = self.sheet_names_column
            self.automode.sheet_trends_column = self.sheet_trends_column
            self.automode.sheet_results_column = self.sheet_results_column
            self.automode.sheet_new_column = self.sheet_new_column
            self.automode.sheet_header_rewrite = self.sheet_header_rewrite
            self.automode.header_config = [(0, 'Build and Device info'),  # sheet header configuration
                                           ('Date', 'Date'),
                                           ('HW', 'HW Barcode'),
                                           ('EMMC|UFS', 'Storage type'),
                                           ('CPU', 'CPU revision'),
                                           ('TST.*CR', 'TST-CR', self.test_cr)]
            self.automode.prepareSheet()

    @classmethod
    def tearDownClass(cls):
        # return battery levels control to previous value
        CONFIG.DEVICE.BATTERY_CONTROL_LEVELS = cls.battery_levels

    def tearDown(self):
        self.iozone.powerUpReason()
        # update results to google sheet
        self.iozone.syslogger.warn(self.iozone.iozone_results.gsheet_results)
        if self.auto and len(self.iozone.iozone_results.gsheet_results) > 1:
            self.automode.updateResults(self.iozone.iozone_results.gsheet_results)

    @OwnLoop()
    def test01(self):
        """ data """
        res, msg = self.iozone.launch(partition='/data', platform=self.platform, thread_size=self.thread_size,
                                      cycles=self.data_cycles, delay=self.data_delay, timeout=self.data_timeout,
                                      verbose=self.verbose)
        self.assertTrue(res, msg)

    @OwnLoop()
    def test02(self):
        """ storage  """
        part = '/storage/emulated/legacy/'
        try:
            self.iozone.sh('ls /storage/emulated/legacy/', errors=True, empty=True)
        except:
            part = '/storage/emulated/0/'
        res, msg = self.iozone.launch(partition=part, platform=self.platform, thread_size=self.thread_size,
                                      cycles=self.storage_cycles, delay=self.storage_delay,
                                      timeout=self.storage_timeout, verbose=self.verbose)
        self.assertTrue(res, msg)

    @OwnLoop()
    def test03(self):
        """ sdcardexternal """
        if self.thread_size is None:
            self.thread_size = 1

        # FBE feature on Eagle
        if 'msm8998' in CONFIG.DEVICE.CPU_HW:
            partition = '/mnt/media_rw/'
        else:
            partition = '/mnt/runtime/default/'

        res, msg = self.iozone.launch(partition=partition, platform=self.platform, thread_size=self.thread_size,
                                      cycles=self.sdcard_cycles, delay=self.sdcard_delay,
                                      timeout=self.sdcard_timeout, verbose=self.verbose, sdcard=True)
        self.assertTrue(res, msg)

    @OwnLoop()
    @SkipByDefault()
    def test04(self):
        """ sdcardinternal """
        if self.thread_size is None:
            self.thread_size = 1

        # check SD card mount
        if self.iozone.detectSDCard('/mnt/expand/') is None:
            self.assertTrue(False, 'SD card is N/A or not mounted as internal storage !')

        res, msg = self.iozone.launch(partition='/mnt/expand/', platform=self.platform, thread_size=self.thread_size,
                                      cycles=self.sdcard_cycles, delay=self.sdcard_delay, timeout=self.sdcard_timeout,
                                      verbose=self.verbose, sdcard=True)
        self.assertTrue(res, msg)

    @OwnLoop()
    @SkipByDefault()
    def test05(self):
        """ sdcardprimary """
        if self.thread_size is None:
            self.thread_size = 1

        # check SD card mount
        sdcard = self.iozone.detectSDCard('/mnt/expand/')
        if sdcard is None:
            self.assertTrue(False, 'SD card is N/A or not mounted as internal storage !')
        if not sdcard in self.iozone.shell('mount | grep /mnt/runtime/default/emulated'):
            self.assertTrue(False, 'SD card is not mounted as primary internal storage !')

        res, msg = self.iozone.launch(partition='/mnt/runtime/default/emulated', platform=self.platform,
                                      thread_size=self.thread_size, cycles=self.sdcard_cycles, delay=self.sdcard_delay,
                                      timeout=self.sdcard_timeout, verbose=self.verbose)
        self.assertTrue(res, msg)

    @OwnLoop()
    def test06(self):
        """ memtest """
        res, msg = self.memtest.launch(cycles=self.memtest_cycles, delay=self.memtest_delay,
                                       timeout=self.memtest_timeout, measure_units=self.memtest_units)
        self.assertTrue(res, msg)
