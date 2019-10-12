# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "12/5/2017 5:35 PM"

import copy
import inspect
from ..wait import Wait
from ..tools import Tools
from config import CONFIG
from libs.core.logger import getSysLogger
from ..exceptions import TestCaseNotFoundError
from libs.core.template import NAME, SUITE_FULL


class Case:
    """
    UnitTest filter class
    """

    @staticmethod
    async def filter_by_cases(case_options):
        """
        Prepare TestCase launch and filter it by TestCases. TestCase delimiter should be comma **,**

        Warning:
            All TestCases will be selected if `case_options` is None

        Args:
            case_options (str or None): String line of selected TestCases

        Function add TestCase filter.

        Filters:
            - filter_by_cases: When TestCase were filtered according to options

        Raises:
            TestCaseNotFoundError: If TestCase not found.
        """
        await Wait.wait_for_available_cases()

        tmp = []
        loader = None
        syslogger = None
        case_list = Tools.convert_str_cases_to_list(case_options)
        if len(case_list) > 0:
            for i, case_name in enumerate(case_list):
                if case_name not in CONFIG.UNITTEST.AVAILABLE_TEST_CASES:
                    raise TestCaseNotFoundError('%s TestCase not found !' % NAME.safe_substitute(name=case_name))
                else:
                    copy_case = copy.deepcopy(CONFIG.UNITTEST.AVAILABLE_TEST_CASES[case_name])
                    copy_case['index'] = i+1

                    # check duplicates
                    if case_name in case_list[:i]:
                        # reload suite classes for duplicates
                        for suite in copy_case['suites']:
                            if loader is None:
                                from libs.core.unittest.scan.scancases import ScanCases
                                loader = ScanCases()
                                syslogger = getSysLogger()
                            syslogger.info('Reloading %s class for %s TestSuite !'
                                           % (NAME.safe_substitute(name=suite['class'].__name__),
                                              SUITE_FULL.safe_substitute(case=case_name, suite=suite['name'], index=i)))
                            cls, _ = await loader.get_suite_class_and_doc(
                                (case_name, None, copy_case['path'], suite['name'], suite['path']),
                                module='.'.join(suite['class'].__module__.split('.')[:-1]))
                            suite['class'] = cls
                    tmp.append(copy_case)
        else:
            # add all tests
            for i, case in enumerate(sorted(CONFIG.UNITTEST.AVAILABLE_TEST_CASES)):
                copy_case = copy.deepcopy(CONFIG.UNITTEST.AVAILABLE_TEST_CASES[case])
                copy_case['index'] = i+1
                tmp.append(copy_case)

        # TestCases not found
        if len(tmp) == 0:
            raise TestCaseNotFoundError('No one TestCase found !')

        # add filter to all cases
        filter_name = inspect.getframeinfo(inspect.currentframe()).function
        for case in tmp:
            case['filters'].append(filter_name)

        # Keep filtered tests to config
        CONFIG.UNITTEST.SELECTED_TEST_CASES = tuple(tmp)
