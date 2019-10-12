# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/27/17 14:58"

import re
import os
from .base import Base
from libs.core.register.base.exceptions import ConfigError
from libs.core.template import SUITE_FULL


class System(Base):
    """
    System default config.
    This config is part of :class:`src.libs.core.register.Register`
    """

    #: Framework debug mode
    DEBUG = False
    #: Framework super debug mode. In this mode some features may be disabled
    SDEBUG = False

    #: path to logs folder
    LOG_PATH = None
    #: logs name prefix
    LOG_PREFIX = ''
    #: File logs size limit in Mb
    LOG_FILE_SIZE_LIMIT = 100
    #: Is logger was initialized
    INITIALIZED = False

    #: System variable with path framework resources
    ENVIRONMENT_VARIABLE = 'ATFRAMEWORK'

    #: Combine external and main config files
    #: True: Use (string, int, float or None) options from local config if available
    #: and combine (list, dict) options with local config priority.
    #: False: Ignore main config option if option exists in local.
    EXTERNAL_CONFIG_COMBINE_WITH_MAIN = False

    #: Current timezone. Most usage: `America/Chicago`.
    #: To print more timezones use the following commands: import pytz; for tz in pytz.all_timezones: print(tz);
    TIMEZONE = 'America/Chicago'

    def __init__(self):
        super(System, self).__init__()
        # root dir
        self.__root_dir = None
        # cycles
        self.__current_cycle_global = 0
        self.__total_cycles_global = 1
        # Warning list printing after all tests.
        self.__warnings = {}
        # Jenkins list printing to Jenkins job and use to send to Email
        self.__jenkins = []

    @property
    def JENKINS(self):
        """
        Jenkins and Email special messages

        Dict structure:

            .. code-block:: python

                {'msg': str,      # Message
                 'level': int,    # logger level
                 'secured': bool  # Is message secured and cannot be send via regular Email client
                }

        Returns:
            dict list
        """
        return self.__jenkins

    @property
    def WARNINGS(self):
        """
        Framework warnings dict

        Returns:
            string list
        """
        return ['[%d] %s' % (self.__warnings[x], x) for x in self.__warnings]

    @property
    def TOTAL_CYCLES_GLOBAL(self):
        """
        Global total cycles property. Total cycles for run test suite

        Returns:
            int: cycle
        """
        return self.__total_cycles_global

    @property
    def CURRENT_CYCLE_GLOBAL(self):
        """
        Global current cycle. Run cycles of test suite.

        Returns:
            int: total cycles count
        """
        return self.__current_cycle_global

    @property
    def ROOT_DIR(self):
        """
        Root Framework directory.

        Returns:
            str: path to root dir
        """

        if self.__root_dir is None:
            tmp = os.path.abspath(__file__)
            for x in range(4):
                tmp = os.path.split(tmp)[0]
            self.__root_dir = tmp
        return self.__root_dir

    @JENKINS.setter
    def JENKINS(self, value):
        """
        Jenkins or Email special list setter

        Args:
            value (str or tuple): String message or tuple (msg, level, secured)

        Convert value to dict with following structure:
            {'msg': str,      # Message
             'level': int,    # logger level
             'secured': bool  # Is message secured and cannot be send via regular Email client
             }
        """
        import logging
        msg = value[0] if isinstance(value, tuple) else value
        level = value[1] if isinstance(value, tuple) and len(value) > 1 and isinstance(value[1], int) else None
        secured = value[2] if isinstance(value, tuple) and len(value) > 2 and isinstance(value[2], bool) \
            else value[1] if len(value) > 1 and level is None else False
        self.__jenkins.append({'msg': msg, 'level': level or logging.INFO, 'secured': secured})

    @WARNINGS.setter
    def WARNINGS(self, msg):
        """
        Framework warnings dict settet
        """
        from config import CONFIG
        msg = '%s - %s <%s:%s:%s>' % (re.sub('[\n\t\r]+', '', msg),
                                      SUITE_FULL.safe_substitute(case=CONFIG.TEST.CURRENT_CASE,
                                                                 index=CONFIG.TEST.CURRENT_CASE_INDEX,
                                                                 suite=CONFIG.TEST.CURRENT_SUITE),
                                      CONFIG.TEST.CURRENT_STATE,
                                      CONFIG.TEST.CURRENT_TEST,
                                      CONFIG.SYSTEM.CURRENT_CYCLE_GLOBAL)
        if msg not in self.__warnings:
            self.__warnings[msg] = 1
        else:
            self.__warnings[msg] += 1

    @TOTAL_CYCLES_GLOBAL.setter
    def TOTAL_CYCLES_GLOBAL(self, value):
        """
        GLOBAL_TOTAL_CYCLE setter.
        Must be > 0 and > GLOBAL_CURRENT_CYCLE.

        Args:
             value (int): cycles
        """
        if not isinstance(value, (int, float)) or self.__total_cycles_global < 1 \
                or self.__total_cycles_global < self.__current_cycle_global:
            raise ConfigError('TOTAL_CYCLES_GLOBAL should be integer in [1-...] range.')

        self.__total_cycles_global = int(value)

    @CURRENT_CYCLE_GLOBAL.setter
    def CURRENT_CYCLE_GLOBAL(self, value):
        """
        GLOBAL_CURRENT_CYCLE setter.
        Must be > 0 and <= GLOBAL_TOTAL_CYCLE.

        Args:
             value (int): cycle
        """
        if not isinstance(value, (int, float)) or self.__current_cycle_global < 0 \
                or self.__current_cycle_global > self.__total_cycles_global:
            raise ConfigError('CURRENT_CYCLE_GLOBAL should be integer in [0-TOTAL_CYCLES_GLOBAL] range.')

        self.__current_cycle_global = int(value)
