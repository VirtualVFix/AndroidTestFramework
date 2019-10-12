# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/26/17 17:20"


class DefaultConfig:
    """
    Default config file.
    """
    #: System default settings
    class System:
        # --------------------------------------------------------------------------
        # Framework settings.
        # --------------------------------------------------------------------------
        #: System variable with path framework resources
        ENVIRONMENT_VARIABLE = 'BSPFRAMEWORK'
        #: Local config file located by ENVIRONMENT_VARIABLE path
        EXTERNAL_CONFIG = ('externalconfig.py', 'ExternalConfig')
        #: Combine external and main config files
        #: True: Use (string, int, float or None) options from local config if available
        #: and combine (list, dict) options with local config priority.
        #: False: Ignore main config option if option exists in local.
        EXTERNAL_CONFIG_COMBINE_WITH_MAIN = False
        #: To print more timezones use: import pytz; for tz in pytz.all_timezones: print(tz);
        TIMEZONE = 'America/Chicago'
        #: Default log file. Uses when logger not initialized
        # DEFAULT_LOGFILE = datetime.now(pytz.timezone(TIMEZONE)).strftime('%H:%M:%S') + '_sys.log'

    #: Device default settings
    class Device:
        # --------------------------------------------------------------------------
        # Device control settings
        # --------------------------------------------------------------------------
        BATTERY_CONTROL = True  #: Enable battery control ("--disable-battery-control" option).
        BATTERY_CONTROL_LEVELS = [70, 90]  #: Battery level thresholds ("--battery-levels" option).
        DAEMON_CHECK_TIME = 1  #: Check time in seconds for collect statistics daemon (if "enable_statistics" option in use).
        # --------------------------------------------------------------------------
        # Temperature settings
        # --------------------------------------------------------------------------
        ENABLE_TEMPERATURE_CONTROL = True  #: Enable temperature control ("--disable-temperature-control" option)
        """ 
        Thermal sensors for temperature control. 
        Sensors are selected automatically by device platform. 
        Sensor from 'default' sector will be used if platform is not specified. 
        """
        THERMAL_SENSOR = {'default': None,
                          'msm8992': ['/sys/devices/virtual/thermal/thermal_zone14/temp',
                                      '/sys/class/hwmon/hwmon2/device/quiet_therm'],
                          'apq8084': ['/sys/class/hwmon/hwmon2/device/apq_therm',
                                      '/sys/class/hwmon/hwmon2/device/apq_therm', 1, 2, 4, 5, 7, 8, 9, 10],
                          'msm8994': ['/sys/devices/virtual/thermal/thermal_zone14/temp',
                                      '/sys/class/hwmon/hwmon3/device/pm_therm', 0, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                          'msm8939': ['/sys/class/hwmon/hwmon1/device/msm_therm', 3, 5, 6, 7, 8, 9],
                          'msm8916': ['/sys/class/hwmon/hwmon1/device/msm_therm', 2, 4, 5],
                          'msm8974': [4, 5, 6, 7, 8, 9, 10],
                          'msm8960': [0, 2, 4],
                          'msm8610': [0, 1],
                          'msm8226': [1, 3],
                          'msm8952': ['/sys/class/thermal/thermal_zone5/temp', 0, 2, 4, 5, 6, 7, 8, 9, 10],
                          'msm8953': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
                          'msm8996': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15,
                                      '/sys/class/thermal/thermal_zone29/temp',
                                      '/sys/class/hwmon/hwmon3/device/quiet_therm'],
                          'msm8937': ['/sys/class/thermal/thermal_zone5/temp', '/sys/class/thermal/thermal_zone18/temp', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                          'msm8998': [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 14, 15, 16, 17, 18, 19, 20, 21, 'battery',
                                      'pm8005_tz', 'pmi8998_tz', 'pm8998_tz', 'msm_therm', 'ufs_therm', 'quiet_therm'],
        }
        SLEEP_TIME_WITHOUT_SENSOR = 300  #: Sleep time for temperature control if thermal sensor is N/A in THERMAL_SENSOR variable.
        COOLING_TIMEOUT = 600  #: Cooling timeout. Test starts if cooling timeout expired.
        """
        Maximal temperature when test can be started with temperature control enabled. 
        Temperature is selected automatically by device product name. 
        Temperature from 'all' sector will be used If product name is not specified.
        """
        RUN_TEMPERATURE = {'default': 40}
        # --------------------------------------------------------------------------
        # Mods settings
        # --------------------------------------------------------------------------
        MODS_ENABLE = False  #: enable mods if available. Use "--enable-mods" launch options
        MODS_PATH = '/sys/class/display/display0/notify'  #: path for on/off mods
        MODS_ON_OFF = {'on': 'connect', 'off': 'disconnect'}  #: command for on/off mods
        #: -------------------------------------------------------------------------
    #: Tests default settings
    class Test:
        # --------------------------------------------------------------------------
        # Flash build settings
        # --------------------------------------------------------------------------
        BUILD_FOLDER = '/BUILDS/'  #: Build folder. This variable used in flash tests if path to build is not specified.
        BUILD_DOWNLOAD_WAIT_TIME = 2 * 60 * 60  #: Time limit for build downloading in seconds.
        # --------------------------------------------------------------------------
        # GOOGLE spreadsheet settings for benchmarks full automate mode
        # May be selected by device name or device platform
        # --------------------------------------------------------------------------
        BENCHMARK_AUTO = {'NAME': {'SheetID': None, 'SheetTab': None, 'MasterCR': None}}
        #: GOOGLE spreadsheet for iozone
        STORAGE_AUTO = {'NAME': {'SheetID': None, 'SheetTab': None, 'MasterCR': None}}
        #: GOOGLE spreadsheet for stress tests
        STRESS_AUTO = {'NAME': {'SheetID': None, 'SheetTab': None, 'SuspendMasterCR': None, 'PUPDMasterCR': None}}
        # --------------------------------------------------------------------------
        # Setup settings
        # --------------------------------------------------------------------------
        #: List of available wifi points. Example [(point name, point password or None)]
        WIFI_POINTS = [('POINT', 'PASSWD')]
        #: List of IP address for ping internet connection
        PING_ADDRESS_LIST = ['google.com',
                             '216.58.216.238']
        PING_TIMEOUT = 30  #: Ping timeout in seconds.


# Ignore to load config from Register config and doc directory
# if os.path.abspath('.').endswith(os.sep + 'doc'):
#     CONFIG = None
# elif
if __name__ not in ['register', 'registerloader']:
    from libs.core.register import Register
    CONFIG = Register()
