# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/26/17 17:20"


class ExternalConfig:
    """
    External framework config.
    Current settings will be replaces or added to Main config file.
    """
    # --------------------------------------------------------------------------
    # Framework settings. (These settings change automatically).
    # --------------------------------------------------------------------------
    class System:
        #: To print more timezones use: import pytz; for tz in pytz.all_timezones: print(tz);
        TIMEZONE = 'America/Chicago'

    class Test:
        # --------------------------------------------------------------------------
        # Flash build settings
        # --------------------------------------------------------------------------
        #: Build folder. This variable used in flash tests if path to build is not specified.
        BUILD_FOLDER = 'D:\\android\\SW\\griffin\\'
        #: Time limit for build downloading in seconds.
        BUILD_DOWNLOAD_WAIT_TIME = 2*60*60
        # --------------------------------------------------------------------------
        # GOOGLE spreadsheet settings for benchmarks full automate mode
        # Can be selected by device name or device platform
        # --------------------------------------------------------------------------
        #: GOOGLE spreadsheet settings for benchmarks full automate mode
        BENCHMARK_AUTO = {'test': {'SheetID': 'SomeSpreadSheetID', 'MasterCR': None}}
        BENCHMARK_AUTO.update(dict.fromkeys(['msm8952', 'ProductName', 'BoardName', 'DeviceName'], {'SheetID': 'SomeSpreadSheetID', 'MasterCR': None}))
        BENCHMARK_AUTO.update(dict.fromkeys(['msm8996', 'ProductName', 'BoardName', 'DeviceName'], {'SheetID': 'SomeSpreadSheetID', 'MasterCR': None}))
        #: GOOGLE spreadsheet settings for iozone full automate mode
        STORAGE_AUTO = {'test': {'SheetID': 'SomeSpreadSheetID', 'MasterCR': None}}
        STORAGE_AUTO.update(dict.fromkeys(['msm8952', 'ProductName', 'BoardName', 'DeviceName'], {'SheetID': 'SomeSpreadSheetID', 'MasterCR': None}))
        STORAGE_AUTO.update(dict.fromkeys(['msm8996', 'ProductName', 'BoardName', 'DeviceName'], {'SheetID': 'SomeSpreadSheetID', 'MasterCR': None}))

        #: GOOGLE spreadsheet for stress tests
        STRESS_AUTO = {'test': {'SheetID': 'SpreadSheetID', 'SuspendMasterCR': None, 'PUPDMasterCR': None}}
        # --------------------------------------------------------------------------
        # Setup wizard and setup settings
        # --------------------------------------------------------------------------
        #: List of available wifi points. Example [(point name, point password or None)]
        WIFI_POINTS = [('PointName', 'PointPassword'),
                       ('AlternativePointName', 'AlternativePointPassword')]
        # --------------------------------------------------------------------------
        #: List of IP address for ping internet connection
        PING_ADDRESS_LIST = ['173.194.122.255',
                             'google.com',
                             '216.58.216.238',  # google.com
                             '93.158.134.11']   # yandex.ru
        # --------------------------------------------------------------------------
