# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/22/17 15:22"

import re
from time import time
from config import CONFIG
from libs.core.template import NAME
from libs.core.logger import getLogger, getSysLogger
from libs.cmd.implement.exceptions import PropertyError
from .implement.constants import PROPERTY_CACHE_TIMEOUT


class Property:
    """
    Provide access to ``adb shell getprop`` or ``fastboot getvar all``
    properties depends of current device state: ``adb`` or ``fastboot``
    """

    def __init__(self, manager, logger=None):
        """
        Args:
            adb (object): ADB object
            fastboot (object): Fastboot object
            logger (logging): Logger
        """
        self.cacheTimeout = PROPERTY_CACHE_TIMEOUT
        self.logger = logger or getLogger(__file__)
        self.syslogger = getSysLogger()
        self.__manager = manager
        self.__cachedTime = 0
        self.__getAdbPropCache = {}
        self.__getFbVarCache = {}

    def __parse_adb_prop(self, props):
        """
        Parse adb properties from cached and stored it to local variable

        Args:
            props (str): All properties from ADB
        """
        self.__cachedTime = time()
        self.__getAdbPropCache = {}
        for name, val in re.findall('(.*?):(.*?)\n', props.replace('[', '').replace(']', ''), re.DOTALL):
            self.__getAdbPropCache[name.replace('\n', '').strip()] = val.strip()

    def __parse_fb_vars(self, vars):
        """
        Parse fastboot variables and keep it to local variable

        Args:
             vars (str): All vars from fastboot
        """
        self.__cachedTime = time()
        self.__getFbVarCache = {}
        for name, val in re.findall('(.*?):\s(.*?)\n', vars.replace('(bootloader)', ''), re.DOTALL):
            name = name.strip()
            if '[' in name:
                name = name[:name.find('[')]
            if name in self.__getFbVarCache:
                self.__getFbVarCache[name] += val.strip() if 'not found' not in val.lower() else ''
            else:
                self.__getFbVarCache[name] = val.strip() if 'not found' not in val.lower() else ''

    def __check_cache(self, force=False):
        """
        Check if cache update required

        Args:
            force (bool): Force update cach
        """
        try:
            if force or ((time() - self.__cachedTime) > self.cacheTimeout):
                mode = self.__manager.get_mode(timeout=60)
                if mode == 'adb':
                    self.__parse_adb_prop(self.__manager.sh('getprop', error=False))
                else:
                    self.__parse_fb_vars(self.__manager.fb('getvar all', error=False))
        except Exception as e:
            self.syslogger.exception(e)
            if CONFIG.SYSTEM.DEBUG is True:
                raise PropertyError(e) from e

    def update_cache(self):
        """ force update properties and variables cache """
        self.__check_cache(force=True)

    def get_prop(self, prop):
        """
        Get adb shell property from cache by name

        Args:
            prop (str): Property name

        Returns:
            str: Found property or None
        """
        self.__check_cache()
        if prop in self.__getAdbPropCache:
            return self.__getAdbPropCache[prop]
        return None

    def get_all_props(self):
        """
        Get all ADB properties from cache
        """
        self.__check_cache()
        if self.__getAdbPropCache != {}:
            return self.__getAdbPropCache
        return None

    def get_var(self, var):
        """
        Get fastboot variable from cache by name

        Args:
            var (str): Variable name

        Returns:
            str: Found var or None
        """
        self.__check_cache()
        if var in self.__getFbVarCache:
            return self.__getFbVarCache[var]
        return None

    def get_all_vars(self):
        """ get all fastboot variables from cache """
        self.__check_cache()
        if self.__getFbVarCache != {}:
            return self.__getFbVarCache
        return None

    # device info
    def getBuildFingerprint(self):
        res = (self.get_prop('ro.build.fingerprint') or '') \
              or (self.get_var('ro.build.fingerprint') or '')
        return res.lower()

    def getDeviceName(self):
        res = (self.get_prop('ro.product.device') or '') \
              or (self.get_prop('ro.hw.device') or '') \
              or (self.get_var('product') or '')
        return res.lower()

    def getProductBuild(self):
        res = self.getBuildFingerprint()
        if res != '':
            res = res.split('/')[2]
            res = res[:res.find(':')]
        return res

    def getProductName(self):
        res = self.getBuildFingerprint()
        if res != '':
            res = res.split('/')[1]
        return res

    def getBuildType(self):
        res = self.getBuildFingerprint()
        if res != '':
            res = res.split('/')[4]
            res = res[res.find(':') + 1:]
        return res

    def getBuildVersion(self):
        res = self.getBuildFingerprint()
        if res != '':
            res = res.split('/')
            res = '%s_%s' % (res[3], res[4][:res[4].find(':')])
        return res

    def getBuildRelease(self):
        res = self.getBuildFingerprint()
        if res != '':
            res = res.split('/')[2]
            res = res[res.find(':') + 1:]
        return res

    def getBuildDescription(self):
        res = self.getBuildFingerprint()
        if res != '':
            res = res.split('/')
            res = '%s-%s %s %s %s %s' % (res[1], res[4][res[4].find(':') + 1:],
                                         res[2][res[2].find(':') + 1:], res[3],
                                         res[4][:res[4].find(':')], res[5])
        return res

    def getCPUHW(self):
        res = (self.get_prop('ro.board.platform') or '') \
              or (self.get_var('cpu') or '')
        return res.lower()

    def getEMMC(self):
        res = (self.get_var('emmc') or '') \
              or (self.get_var('ufs') or '')
        return res.lower()

    def getUFS(self):
        return self.getEMMC()

    def isCPU64Bit(self):
        res = self.get_prop('ro.product.cpu.abilist64')
        if res is None:
            self.logger.warnlist('There is not alternative for %s property in FASTBOOT mode !'
                                 % NAME.safe_substitute(name='ro.product.cpu.abilist64'), self.syslogger)
        return True if res is not None and res != '' else False

    def isProductBuild(self):
        pass

    def getRevisionHW(self):
        res = (self.get_prop('ro.hw.revision') or '') \
              or (self.get_prop('ro.revision') or '') \
              or (self.get_prop('ro.hw.hwrev') or '') \
              or (self.get_var('hwrev') or '')
        return res.lower()
