# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Mar 6, 2015 11:11:20 AM$"

import os

# Iozone apk directory
HOME_DIR = os.path.split(os.path.split(os.path.realpath(os.path.dirname(__file__)))[0])[0]
APKS_DIR = os.path.join(HOME_DIR, 'apk')

#: Utility install path on device
INSTALL_PATH = '/data/local/tmp/'
#: Memtest util name for x64
MEMTEST_UTIL64 = 'memtest'
#: Memtest util name for x32
MEMTEST_UTIL32 = 'memtest'
#: Memtest util name for launch
MEMTEST_NAME = 'memtest'
#: Memtest results field counter
MEMTEST_FILED_COUNT = 6
#: Sorted measure units for memtest
FS_PERFORMANCE_MEASURE_UNITS = ['KB', 'MB', 'GB', 'TB', 'PB', 'EB']
