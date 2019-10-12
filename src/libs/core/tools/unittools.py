# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/19/17 14:53"

import types
import asyncio
import platform
from config import CONFIG
from unittest import SkipTest
from libs.core.unittest import Wait
from libs.core.tools import Utility
from .exceptions import UnitSkipError
from libs.core.logger import getLoggers
from .config import ALLOWED_UNIT_SKIP_COMPARE_RULES
from libs.core.unittest.config import FILTERS_NAMES
from libs.core.template import NAME, SUITE_FULL, SUITE


def OwnLoop():
    """
    Decorator for unittest Tests in TestSuite.

    Note:
        May be use for whole Test Class or Test function

    Marks Test have own loop control otherwise Test will be converted to SubTest with required Test cycles.
    """
    def decorator(item):
        item.__own_loop = True
        return item

    return decorator


def PassRate(rate=100, rate_by_total_cycles=False):
    """
    Marks to pass rate of Test.

    Note:
        May be use for whole Test Class or Test function

    Args:
        rate (float or int, Default: 100): Required test pass rate
        use_total_cycle (bool, Default: False): Marks to use total cycle to calculate pass rate otherwise use current cycle.
    """
    def decorator(item):
        try:
            if rate_by_total_cycles is not None:
                item.__rate_by_total_cycles = rate_by_total_cycles
            item.__pass_rate = float(rate)
            if item.__pass_rate < 0 or item.__pass_rate > 100:
                item.__pass_rate = 100
                raise Exception('Value should float or integer be in 0-100 range. '
                                + 'Current value "%s" will be replaced to 100' % rate)
        except Exception as e:
            if CONFIG.SYSTEM.DEBUG is True:
                raise
            logger, syslogger = getLoggers(__file__)
            logger.error('PassRate error of %s Test: %s'
                         % (SUITE.safe_substitute(case=item.__module__, suite=item.__name__), e), syslogger)
        return item
    return decorator


def SkipByDefault(ifPlatform=None, ifDeviceName=None, ifProductName=None, ifAndroidVersion=None,
                  ifSystem=None, rule='=='):
    """
    Unittest skip test decorator. Allow to skip test by device properties depends of current device state
    (adb or fastboot).
    Skip test if it not in launch list or device doesn't meet one of criteria: ifPlatform, ifDeviceName, ifProductName.
    Properties define in :mod:`src.libs.cmd.property` module.

    Args:
        ifPlatform (str or list): Skip by "`ro.board.platform`" in adb or "`cpu`" option in fastboot (Default: None).
        ifDeviceName (str or list): Skip by "`ro.hw.device`", "`ro.product.device`" in adb or "`product`" option
            in fastboot (Default: None).
        ifProductName (str or list): Skip by "`ro.product.name`" in adb or product name in "`ro.build.fingerprint`"
            option (Default: None).
        ifAndroidVersion (str): Skip by version of android. (Default: None)
        ifSystem (str): OS where Framework was launched (linux or windows)
        rule (str, one of [<, >, =, <=, >=, !=]): Android version compare gate_rule.
        For criteria instead of ifAndroidVersion work "=" or "!=" gate_rules only.

    Returns:
        decorated function

    Example:

    .. code-block:: python

        @SkipByDefault(ifPlatform='MSM8996', gate_rule='==')
        def test01(self):
            self.assertEqual(True, True)

    Warning:
        May be use for Test function only !

    Note:
        Criteria priority: ifAndroidVersion, ifPlatform, ifDeviceName, ifProductName
    """

    def find_test_suite(test_hash, test_name):
        """
        Find TestSuite by TestCase name and TestSuite name

        Args:
             test_hash (int): Hash of Test function to find it in config
             test_name (str): Test name

        Returns:
            (TestCase dict, TestSuite dict) when found Test or (None, None) if Test not found
        """
        for case in CONFIG.UNITTEST.SELECTED_TEST_CASES:
            for suite in case['suites']:
                if id(getattr(suite['class'], test_name, False)) == test_hash:
                    return case, suite
        return None, None

    def decorator(item):
        # loggers
        logger, syslogger = getLoggers(__file__)
        # ignore not function object
        if not isinstance(item, types.FunctionType):
            logger.error('SkipByDefault decorator object type error: expected - %s, found - %s'
                         % (NAME.safe_substitute(name=types.FunctionType),
                            NAME.safe_substitute(name=type(item))), syslogger)
            return item

        # async skip check
        async def async_skip_test(test_item):
            await Wait.wait_for_load_tests()
            reason = 'Skipped by default'  # skip reason
            skip = True  # skip is required
            try:
                # check compare gate_rules
                if rule not in ALLOWED_UNIT_SKIP_COMPARE_RULES:
                    raise UnitSkipError('Inconsistent "%s" compare gate_rule parameter ! ' % rule
                                        + 'Allowed the following gate_rules: [%s]'
                                        % ','.join(ALLOWED_UNIT_SKIP_COMPARE_RULES))

                # ignore skip if TestSuite not found or Tests were included selected by user
                case, suite = find_test_suite(id(test_item), test_item.__name__)
                if suite is None or FILTERS_NAMES['set_tests_include'] in suite['filters']:
                    return

                # wait for device
                await Wait.wait_for_device()

                # use for xnor to include or exclude value
                gate_rule = False if rule == '!=' else True
                # android
                if ifAndroidVersion is not None:
                    _list = ifAndroidVersion if isinstance(ifAndroidVersion, list) else [ifAndroidVersion]
                    from pkg_resources import parse_version
                    for x in _list:
                        tmp = 'parse_version(str(CONFIG.DEVICE.BUILD_RELEASE)) %s parse_version(str(x))' % rule
                        if eval(tmp):
                            reason = 'Skipped due to Android version %s %s' % (rule, x)
                            break
                    else:
                        skip = False
                # platform
                elif ifPlatform is not None:
                    _list = ifPlatform if isinstance(ifPlatform, list) else [ifPlatform]
                    for x in _list:
                        if not (x.lower() in CONFIG.DEVICE.CPU_HW.lower()) ^ gate_rule:
                            reason = 'Skipped due to platform %s %s' % (rule, x)
                            break
                    else:
                        skip = False
                # product
                elif ifProductName is not None:
                    _list = ifProductName if isinstance(ifProductName, list) else [ifProductName]
                    for x in _list:
                        if not (x.lower() in CONFIG.DEVICE.DEVICE_PRODUCT.lower()) ^ gate_rule:
                            reason = 'Skipped due to product name %s %s' % (rule, x)
                            break
                    else:
                        skip = False
                # device
                elif ifDeviceName is not None:
                    _list = ifDeviceName if isinstance(ifDeviceName, list) else [ifDeviceName]
                    for x in _list:
                        if not (x.lower() in CONFIG.DEVICE.DEVICE_NAME.lower()) ^ gate_rule:
                            reason = 'Skipped due to device name %s %s' % (rule, x)
                            break
                    else:
                        skip = False
                elif ifSystem is not None:
                    _list = ifSystem if isinstance(ifSystem, list) else [ifSystem]
                    for x in _list:
                        if not (x.lower() in platform.system().lower()) ^ gate_rule:
                            reason = 'Skipped due to OS %s %s' % (rule, x)
                            break
                    else:
                        skip = False

                # skip Test
                if skip is True:
                    def skip_wrapper(*args, **kwargs):
                        raise SkipTest(reason)

                    skip_wrapper.__unittest_skip__ = True
                    skip_wrapper.__unittest_skip_why__ = reason
                    setattr(suite['class'], test_item.__name__, skip_wrapper)

                    syslogger.debug('Test %s of %s TestSuite was marked as skip with "%s" reason'
                                    % (NAME.safe_substitute(name=test_item.__name__),
                                       SUITE_FULL.safe_substitute(case=case['name'], index=case['index'],
                                                                  suite=suite['name']), reason), logger)
            except Exception as e:
                syslogger.exception(e)
                if CONFIG.SYSTEM.DEBUG is True:
                    logger.exception(e)
                else:
                    logger.error(Utility.error_to_message(e))

        # get event loop
        event_loop = asyncio.get_event_loop()
        if event_loop.is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())

        # create async detect device task
        asyncio.gather(asyncio.async(async_skip_test(item)))

        return item
    return decorator
