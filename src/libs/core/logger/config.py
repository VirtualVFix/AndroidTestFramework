# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "29/09/17 11:25"

import re
import os
import logging
import platform
from datetime import datetime
from libs.core.singleton import Singleton


class LEVEL:
    """
    Logger levels static class
    """
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    CRITICAL = logging.CRITICAL


class LocalConfig(metaclass=Singleton):
    """
    Logger local config
    """
    #: Debug mode. Synchronized with CONFIG.SYSTEM.DEBUG when logger initialized
    DEBUG = False

    #: Is logger was initialized
    INITIALIZED = False

    #: file extensions. Uses for remove extensions when __file__ uses as logger name.
    FILE_EXTENSIONS = ('.py', '.pyc', '.red')

    #: system logger file name
    SYS_LOGGER_FILE_NAME = 'sys.log'

    #: default output file name
    DEFAULT_LOGGER_FILE_NAME = 'out.log'

    #: Max path length to log directory
    LOG_DIR_LENGTH_PATH = 252

    #: File logs size in Mb
    LOG_FILE_SIZE_LIMIT = 100

    #: Message prints with .done() command
    DONE_MESSAGE = 'Done'

    #: Logger level names
    LOGGER_LEVEL_MAP = {
        logging.NOTSET:   'N',
        logging.DEBUG:    'D',
        logging.INFO:     'I',
        logging.WARN:     'WARN',
        logging.ERROR:    'ERROR',
        logging.CRITICAL: 'CRITICAL'
    }

    #: Log dir datetime format
    LOG_DIR_DATE_FORMAT = '%m.%d.%y_%H-%M-%S_'

    #: File log format
    FILE_LOG_FORMAT = '%(asctime)s %(levelname)s/%(module)s/%(funcName)s/%(name)s: %(message)s'
    FILE_LOG_DATE_FORMAT = '%m-%d %H:%M:%S'

    #: Jenkins log format
    JENKINS_LOG_FORMAT = '%(asctime)s %(levelname)s/%(name)s: %(message)s'
    JENKINS_LOG_DATE_FORMAT = '%m-%d %H:%M:%S'

    #: Console log format
    CONSOLE_LOG_FORMAT = '%(levelname)s/%(name)s: %(message)s'
    CONSOLE_LOG_DATE_FORMAT = ''

    #: Blank logger format
    BLANK_LOGGER_FORMAT = '%(message)s'

    #: console width. Detects automatically when possible
    DEFAULT_CONSOLE_WIDTH = 100
    #: offset when console width was detected
    DEFAULT_CONSOLE_WIDTH_OFFSET = 1
    #: Increase table size in files
    DEFAULT_FILE_LOGGER_OFFSET_DENOMINATOR = 6
    #: Table align when not set in arguments
    TABLE_DEFAULT_ALIGN = 'Left'
    #: Columns delimiter added to column border with regular content
    #: Should be same length with COLUMNS_BORDER_DELIMITER
    TABLE_COLUMNS_DELIMITER = '|'
    #: Border delimiter added to column border with fill line content
    #: Should be same length with COLUMNS_DELIMITER
    TABLE_BORDER_DELIMITER = '+'

    #: Remove list. Logs from this list will be removed before Framework will be stopped
    REMOVE_LIST = []

    def __init__(self):
        self.__default_log_folder = None
        self.__default_file_prefix = None
        self.__console_width = None

        # add level name
        for x in self.LOGGER_LEVEL_MAP:
            logging.addLevelName(x, self.LOGGER_LEVEL_MAP[x])

    @property
    def CONSOLE_WIDTH(self) -> int:
        """
        Console width property.

        Width detects automatically.
        Default value specified in self.DEFAULT_CONSOLE_WIDTH will use if width cannot be detected.

        Todo:
            - Fix "'stty' is not recognized..." error in cmd and powershell console.
        """
        if self.__console_width is None:
            try:
                # linux and cigwin console
                if len(os.popen('stty size', 'r').read().split()) > 0:
                    self.__console_width = int(os.popen('stty size', 'r').read().split()[1]) \
                                           - self.DEFAULT_CONSOLE_WIDTH_OFFSET
                # windows cmd or powershell console
                elif 'window' in platform.system().lower():
                    out = os.popen('for /F "usebackq tokens=2* delims=: '
                                   '" %W in (`mode con ^| findstr Columns`) do set WIDTH=%W').read()
                    match = re.search('width=([\d]+)', out, re.I)
                    if match:
                        self.__console_width = int(match.group(1)) - self.DEFAULT_CONSOLE_WIDTH_OFFSET
            except Exception as e:
                if self.DEBUG:
                    # print due to logger not available
                    print('Error of detect console width: %s' % e)

        if self.__console_width is None:
            self.__console_width = self.DEFAULT_CONSOLE_WIDTH

        return self.__console_width or 20

    @property
    def DEFAULT_LOGS_FOLDER(self) -> str:
        """
        Default logs directory property
        """
        if self.__default_log_folder is None:
            tmp = os.path.abspath(__file__)
            for x in range(5):
                tmp = os.path.split(tmp)[0]
            self.__default_log_folder = os.path.join(tmp, 'logs')
        return self.__default_log_folder

    @property
    def DEFAULT_FILE_PREFIX(self) -> str:
        """
        Default logger file property. Uses in early logger when main logger not initialized
        """
        if self.__default_file_prefix is None:
            self.__default_file_prefix = datetime.now().strftime('%m.%d.%y_%H-%M-%S_%f_')
        return self.__default_file_prefix


if 'core.logger' in __name__:
    LOCAL = LocalConfig()
