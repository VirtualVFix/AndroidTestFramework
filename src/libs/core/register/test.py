# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/27/17 14:58"

from .base import Base


class Test(Base):
    """
    Test default config. This config is part of :class:`src.libs.core.register.Register`
    """

    #: Current test state. Updates automatically during testing
    CURRENT_STATE = ''
    #: Current TestSuite name. Updates automatically during testing
    CURRENT_SUITE = ''
    #: Current Test name. Updates automatically during testing
    CURRENT_TEST = ''
    #: Current TestCase name. Updates automatically during testing
    CURRENT_CASE = ''
    #: Current TestCase index. Updates automatically during testing
    CURRENT_CASE_INDEX = -1

    #: Test name configured by code
    TEST_NAME = ''

    #: Total cycles of current Test.
    #: Changes automatically for each Test and depends of ***_cycles** variable in Test class.
    TOTAL_CYCLES = 1
    #: Current cycle of current Test.
    #: May changes automatically (by default) or directly from Test implementation (@OwnCycle decorator in use)
    CURRENT_CYCLE = 0
    #: Test failed. Used to calculate pass rate when it not depend of test cycle.
    #: Pass rate will be calculate according to complete cycles if == 0
    FAILED_CYCLES = 0
    #: Test pass rate.
    #: May changes automatically (by default) or directly from Test implementation.
    #: Pass rate may be affected by @OwnCycle(use_total_cycle=True) decorator or FAILED_CYCLES variable
    PASS_RATE = 0

    #: ADB implementation by default
    DEFAULT_ADB_IMPLEMENTATION = 'base'
    #: ADB shell implementation by default
    DEFAULT_SHELL_IMPLEMENTATION = 'base'
    #: Fastboot implementation by default
    DEFAULT_FASTBOOT_IMPLEMENTATION = 'base'
    #: CMD implementation by default
    DEFAULT_CMD_IMPLEMENTATION = 'base'

    #: Email address used to send notify
    NOTIFICATION_EMAIL = 'somenotifybot@gmail.com'
    #: Main host. Adds to Email addresses if host not specified
    NOTIFICATION_HOST = '@gmail.com'
    #: Email password. Should be encode in base64
    NOTIFICATION_PWD = b''
    #: Email subject tag
    NOTIFICATION_TAG = '[FRAMEWORK]'
    #: Email addresses list
    NOTIFICATION_MAIL_LIST = []
    #: Additional comment in Email subject
    NOTIFICATION_COMMENT = ''
    #: Email class to send notify
    NOTIFICATION_CLASS = None

    #: Path to build specified in "--build" option. (Variable changes automatically).
    BUILD_PATH = ''
    #: build name tag like "nash_oem"
    BUILD_TAGNAME = None
    #: build job name on Jenkins or Artifactory
    BUILD_JOBNAME = None
    #: Build folder. This variable used in flash tests if path to build is not specified.
    BUILD_FOLDER = '/BUILDS/'
    #: Time limit for build downloading in seconds.
    BUILD_DOWNLOAD_WAIT_TIME = 2 * 60 * 60

    #: List of available wifi points. #[(point name, point password or None)]
    WIFI_POINTS = [('POINT', 'PASSWD')]
    #: List of IP address for ping internet connection
    PING_ADDRESS_LIST = ['google.com', '216.58.216.238']
    #: Ping timeout in seconds for check internet connection
    PING_TIMEOUT = 30

    #: GOOGLE spreadsheet settings for benchmarks full automate mode
    #: May be selected by device name or device platform
    BENCHMARK_AUTO = {'NAME': {'SheetID': None, 'SheetTab': None, 'MasterCR': None}}
    #: GOOGLE spreadsheet for iozone
    STORAGE_AUTO = {'NAME': {'SheetID': None, 'SheetTab': None, 'MasterCR': None}}
    #: GOOGLE spreadsheet for stress tests
    STRESS_AUTO = {'NAME': {'SheetID': None, 'SheetTab': None, 'SuspendMasterCR': None, 'PUPDMasterCR': None}}

    def __init__(self):
        super(Test, self).__init__()
