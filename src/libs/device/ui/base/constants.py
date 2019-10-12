# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Oct 11, 2016 4:09:00 PM$"

import os
from config import CONFIG


# directory of test application
APKS_DIR = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], 'apk') + os.sep
# print info with this label from JUnit instrument output
PRINT_INFO_VALUES = "INSTRUMENTATION_STATUS: PRINT=" 
# print warning with this label from JUnit instrument output 
PRINT_WARN_VALUES = ("AlertWatcher:") 
# AndroidJUnitRunner log file name 
LOG_FILE_NAME = 'junitrunner.log'
# sub results key words
SUBRESULTS_KEY_WORDS = ['SCREENSHOT', 'UIDUMP']
# test app install timeout
INSTALL_TEST_APP_TIMEOUT = 60
# error length ro console output. # unfinity if == 0
ERROR_OUTPUT_LENGTH = 10
# default base apk for UI testing
DEFAULT_BASE_APK = { 
    'name':'JUnit Base',
    'apk':'BenchmarksApp-debug.apk',
    'package': 'kernel.bsp.test.ui.benchmarks',
    'version': '0.0.4',
    'replace': False
}
# default test apk for UI testing
DEFAULT_TEST_APK = {
    'name':'JUnit Test',
    'apk':'BenchmarksApp-debug-androidTest.apk',
    'package': 'kernel.bsp.test.ui.benchmarks.test',
    'version': 'null',
    'replace': True if CONFIG.SYSTEM.DEBUG else False
}

# device control variables
DISPLAY_TIMEOUT_ALLOW_UNITS = ['sec', 'min', 'second', 'minute', 'seconds', 'minutes']
# maximal and minumal display timeouts
MAX_DISPLAY_TIMEOUT_IN_SECONDS = 30*60
MIN_DISPLAY_TIMEOUT_IN_SECONDS = 15
# device control apk settings
DEVICE_SETTINGS = {
    'SkipSetupWizard':{
        'name':'Skip setup wizard',
        'junit': 'kernel.bsp.test.ui.benchmarks.support.SkipWizard',
        'function': 'skipWizard',
        '_iterations': 40, # max iterations before failure skip setup wizard
        '_points': [] # point list from config or local config
    },
    'WiFiStatus':{
        'name':'WiFi status',
        'junit': 'kernel.bsp.test.ui.benchmarks.support.WiFi',
        'function': 'isWiFiEnabled'
    },
    'WiFiEnable':{
        'name':'WiFi enable',
        'junit': 'kernel.bsp.test.ui.benchmarks.support.WiFi',
        'function': 'enableWiFi'
    },
    'WiFiDisable':{
        'name':'WiFi disable',
        'junit': 'kernel.bsp.test.ui.benchmarks.support.WiFi',
        'function': 'disableWiFi'
    },
    'WiFiConnectToPoint':{
        'name':'WiFi disable',
        'junit': 'kernel.bsp.test.ui.benchmarks.support.WiFi',
        'function': 'connectToWiFiPoint',
        '_timeout': 60, # timeout of waiting connection status
        '_points': [] # point list from config or local config
    },
    'MediaVolume':{
        'name':'Mode media volume',
        'junit': 'kernel.bsp.test.ui.benchmarks.support.Sound',
        'function': 'muteMediaVolume'
    },
    'MaxDisplayTimeout':{
        'name':'Set maximum screen timeout',
        'junit': 'kernel.bsp.test.ui.benchmarks.support.Display',
        'function': 'setMaxTimeout'
    },
    'SetDisplayTimeout':{
        'name':'Set screen timeout',
        'junit': 'kernel.bsp.test.ui.benchmarks.support.Display',
        'function': 'setSpecifiedTimeout',
        '_timeout': 15,
        '_unit': 'sec'
    },
    'SetStayAwake':{
        'name':'Set stay awake',
        'junit': 'kernel.bsp.test.ui.benchmarks.support.Debug',
        'function': 'setStayAwake',
        '_enable': True
    },
    'SetScreenLockToNone':{
        'name':'Set screen lock to None',
        'junit': 'kernel.bsp.test.ui.benchmarks.support.Security',
        'function': 'setScreenLockToNone',
    },
    'SetTimeFormat':{
        'name':'Set time format',
        'junit': 'kernel.bsp.test.ui.benchmarks.support.Date',
        'function': 'setTimeFormat',
        '_use24': False
    }
}
