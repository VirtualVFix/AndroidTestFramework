# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__="VirtualV <https://github.com/virtualvfix>"
__date__ = "$Aug 11, 2017 12:20:00 PM$"


BUILD_SERVER                  = 'https://jenkins.mot.com/'
BUILD_SERVER_NAME             = ''
BUILD_SERVER_PASSWORD         = ''  # API Token which can be used instead of the password:it is taken from the Build server (Configure menu->API token section)

SHOW_UNPACK_PROCESS           = False

FILE_TO_FLASH_WINDOWS         = 'flashall.bat'
FILE_TO_FLASH_LINUX           = 'flashall.sh'

RE_PATTERN_COMPARE_BUILDS     = 'motorola/([\w]+)/([\w]+):([\d.]+)/([\w\d.-]+)/([\d]+):([\w]+)/'

DEFAULT_FLASH_TIMEOUT         = 25*60  # flash timeout in seconds
DEFAULT_WAIT_TIMEOUT          = 20*60  # wait device in idle/adb timeout in seconds after flash

MINIMAL_FLASH_OPERATIONS      = 10  # exception will be raised if operation in flash log less this value
MINIMAL_FLASH_TIME            = 30  # minimal time in seconds to flash device. exception will be raised if device was flashed too fast
