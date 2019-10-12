# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Dec 11, 2015 5:57:15 PM$"

import unittest
from config import CONFIG
from libs.device.shell import SDCard
from tests.exceptions import TestPrepareError
from libs.core.tools import SkipByDefault, OwnLoop
from tests.benchmarks.tools.benchmark import Benchmarks


class BenchmarksTestCase(unittest.TestCase):
    """ Test suit """
    # full automate parameters -------------------------------------------------
    auto = False                    # enable full automate mode.
    device = None                   # device name or platform. Spreadsheet will be find by this name. Platform will be detected automatically If == None.
    spreadsheet_id = None           # Spreadsheet ID. It can be specify directly.
    sheet_id = ''                   # Identifier of sheet(tab) Goolge in spreadsheet. It can be index, sheet id or sheet name (string). '0' by default.
    sheet_names_column = 'A'        # Identifier of column with test names. Can be column name or index.
    sheet_trends_column = 'C'       # Identifier of column with trend formula. Can be column name or index.
    sheet_results_column = 'D'      # Identifier of column with values or previous results for compare. Can be column name or index.
    sheet_new_column = True         # Save results to new column. Results will be saved to "sheet_values_column" column if false.
    sheet_header_rewrite = False    # Rewrite already exists header data in "sheet_values_column" when "sheet_insert_new_column" == False
    test_cr = None                  # Temperorary variable for add testCR Link to spreadsheet.
    # --------------------------------------------------------------------------
    prepare = True                  # Prepare device before testing. SkipSetup wizard, set display timeout, mute Media volume
    ignore_sdcard = False           # ignore SD card check. SD card mounted as internal primary can affect performance.
    skip_wizard = True              # skip setup wizard during device preparing if available
    # --------------------------------------------------------------------------
    quadrant_cycles = 10            # Quadrant test cycles
    antutu614_cycles = 10           # Antutu 6.1.4 test cycles
    antutu626_cycles = 10           # Antutu 6.2.6 test cycles
    cfbench_cycles = 5              # CFBench test cycles
    gfxbench_cycles = 1             # GFXBench test cycles
    threedmark_cycles = 1           # 3DMark test cycles
    sunspider_cycles = 1            # Sunspider test cycles
    octane_cycles = 1               # Octane test cycles
    kraken_cycles = 1               # Kraken test cycles
    sdplayinternal_cycles = 10      # SDPlay on internal storage test cycles
    sdplayuserdata_cycles = 10      # SDPlay on userdata test cycles
    androbench_cycles = 10          # Androbench test cycles
    andebenchpro_cycles = 5         # Andebench pro test cycles
    
    @classmethod
    def setUpClass(self):
        self.benchmarks = Benchmarks(CONFIG.DEVICE.SERIAL, device_prepare=self.prepare, skip_wizard=self.skip_wizard)
        
        # check SD card mounted as internal primary
        if not self.ignore_sdcard:
            sdcard = SDCard(CONFIG.DEVICE.SERIAL).detectSDCard('/mnt/expand/')
            if sdcard is not None and sdcard in self.benchmarks.shell('mount | grep /mnt/runtime/default/emulated'): 
                raise TestPrepareError('SD card is mounted as primary internal storage ! It may affect to performance. '
                                       + 'Please unmount SD card as primary or use "-p "ignore_sdcard=true" '
                                       + 'option to ignore check !')

        if not self.auto: # full automation mode
            self.automode = None
        else:
            from tests.benchmarks.tools.automode import AutoMode
            self.automode = AutoMode(serial=CONFIG.DEVICE.SERIAL,
                                     spreadsheet_id=self.spreadsheet_id or CONFIG.propertyByDevice('TEST', 'BENCHMARK_AUTO', self.device, 'SheetID'),
                                     sheet_identifier=self.sheet_id or CONFIG.propertyByDevice('TEST', 'BENCHMARK_AUTO', self.device, 'SheetTab') or '0',
                                     client_file_name='atframeworkkey.json')
            self.automode.sheet_names_column = self.sheet_names_column
            self.automode.sheet_trends_column = self.sheet_trends_column
            self.automode.sheet_results_column = self.sheet_results_column
            self.automode.sheet_new_column = self.sheet_new_column
            self.automode.sheet_header_rewrite = self.sheet_header_rewrite
            # sheet header configuration
            self.automode.header_config = [(0, 'Build and Device info'),
                                           ('Date', 'Date'),
                                           ('HW', 'HW Barcode'),
                                           ('EMMC|UFS', 'Storage type'),
                                           ('CPU', 'CPU revision'),
                                           ('Temperature', 'Temperature', 'less or equal 40C'),
                                           ('SD card', 'SD card', 'No SD card'),
                                           ('TST.*CR', 'TST-CR', self.test_cr)]
            self.automode.prepareSheet()
        
    @classmethod
    def tearDownClass(cls):
        cls.benchmarks.uninstallJunitRunner()
         
    def setUp(self):
        self.benchmarks.powerUpReason()
    
    def tearDown(self):
        self.benchmarks.syslogger.warn(self.benchmarks.bench_results.gsheet_results)
        if self.auto and len(self.benchmarks.bench_results.gsheet_results) > 1: 
            self.automode.updateResults(self.benchmarks.bench_results.gsheet_results)

    @OwnLoop()
    @SkipByDefault(ifPlatform='MSM8996')  # skip this test for Vector
    def test01(self):
        """ Quadrant """
        res, msg = self.benchmarks.launch("Quadrant", cycles=self.quadrant_cycles)
        self.assertTrue(res, msg)

    @OwnLoop()
    @SkipByDefault(ifPlatform='MSM8998', rule='!=')  # launch test for Nash only
    def test05(self):
        """ AnTuTu614 """
        res, msg = self.benchmarks.launch("AnTuTu614", cycles=self.antutu614_cycles)
        self.assertTrue(res, msg)
        
    @OwnLoop()
    def test06(self):
        """ AnTuTu626 """
        res, msg = self.benchmarks.launch("AnTuTu626", cycles=self.antutu626_cycles)
        self.assertTrue(res, msg)

    @OwnLoop()
    def test07(self):
        """ CFBench """
        res, msg = self.benchmarks.launch("CFBench13", cycles=self.cfbench_cycles)
        self.assertTrue(res, msg)

    @OwnLoop()
    def test09(self):
        """ GFXbench """
        res, msg = self.benchmarks.launch("GFXBench4", cycles=self.gfxbench_cycles)
        self.assertTrue(res, msg)

    @OwnLoop()
    def test13(self):
        """ 3DMark """
        res, msg = self.benchmarks.launch("3DMark", cycles=self.threedmark_cycles)
        self.assertTrue(res, msg)

    @OwnLoop()
    def test16(self):
        """ Sunspider """
        res, msg = self.benchmarks.launch("Sunspider102", cycles=self.sunspider_cycles)
        self.assertTrue(res, msg)

    @OwnLoop()
    def test17(self):
        """ Octane """
        res, msg = self.benchmarks.launch("Octane", cycles=self.octane_cycles)
        self.assertTrue(res, msg)

    @OwnLoop()
    def test18(self):
        """ Kraken """
        res, msg = self.benchmarks.launch("Kraken", cycles=self.kraken_cycles)
        self.assertTrue(res, msg)

    @OwnLoop()
    def test19(self):
        """ SDPlayInternal """
        res, msg = self.benchmarks.launch("SDPlayInternal", cycles=self.sdplayinternal_cycles)
        self.assertTrue(res, msg)

    @OwnLoop()
    def test20(self):
        """ SDPlayUserdata  """
        res, msg = self.benchmarks.launch("SDPlayUserdata", cycles=self.sdplayuserdata_cycles)
        self.assertTrue(res, msg)

    @OwnLoop()
    def test21(self):
        """ AndroBench """
        res, msg = self.benchmarks.launch("AndroBench", cycles=self.androbench_cycles)
        self.assertTrue(res, msg)

    @OwnLoop()
    @SkipByDefault(ifAndroidVersion='8.0', rule='>=')  # skip test on Android O and later
    def test23(self):
        """ AndEBenchPro """
        res, msg = self.benchmarks.launch("AndEBenchPro", cycles=self.andebenchpro_cycles, retries=4)
        self.assertTrue(res, msg)
