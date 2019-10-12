# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "12/5/2017 5:36 PM"


import copy
import inspect
from ..wait import Wait
from ..tools import Tools
from config import CONFIG
from libs.core.template import NAME
from libs.core.logger import getLoggers
from ..exceptions import TestSuiteOptionsError, TestSuiteNotFoundError


class Suite:
    """
    UnitTest filter class
    """

    @staticmethod
    def remove_suite_option_duplicates(suite_list):
        """
        Remove duplicates in options list and convert it to tuple

        Args:
            suite_list (list): parsed TestSuite options

        Returns:
            tuple(suite_list) without duplicates
        """
        result = []
        logger, syslogger = getLoggers(__file__)
        for j, suites in enumerate(suite_list):
            tmp = []
            if suites is not None:
                for i, suite in enumerate(suites):
                    if suite is not None and i < len(suites) and suite in suites[i + 1:]:
                        logger.warning('%s TestSuite was duplicated for %s TestCase in launch options ! '
                                       % (NAME.safe_substitute(name=suite),
                                         NAME.safe_substitute(name=CONFIG.UNITTEST.SELECTED_TEST_CASES[j]['name']))
                                       + 'All duplicates will be ignored.', syslogger)
                    else:
                        tmp.append(suite)
            else:
                tmp = None
            result.append(tmp)
        return tuple(result)

    @staticmethod
    async def filter_by_suite(include_option):
        """
        Prepare TestCase launch and filter it by included TestSuites.
        Minus **-** symbol before TestSuite change filter behavior to exclude TestSuite.
        TestSuites set of each TestCases should be delimited by semicolon **;** in same order as TestCases.
        TestSuites inside set should be delimited by comma **,**.

        Note:
            Default TestSuites from *suite.list* file will be ignored If TestSuites included or excluded by option.
            Otherwise only TestSuites from suite.list file will be selected to launch.

        Example:
            --test "testCase1, testCase2" --include "-testSuite1; testSuite1,testSuite2"

        Args:
            include_option (str or None): String line of selected TestSuites

        Function add TestCase filter.

        Filters:
            - filter_by_suite: When TestSuites were filtered according to options

        Raises:
            RuntimeInterruptError: If TestSuite not found.
        """
        await Wait.wait_for_selected_cases()

        suite_list = Tools.convert_str_suites_to_list(include_option)

        # TestSuites sets more than TestCases
        if len(suite_list) > len(CONFIG.UNITTEST.SELECTED_TEST_CASES):
            raise TestSuiteOptionsError('TestSuites select option error: '
                                        + 'Count of sets of TestSuites more than selected TestCases ! '
                                        + 'Use [--help] option to get help of options.')

        # fill list with None according to selected TestCases
        suite_list += [None] * abs(len(suite_list) - len(CONFIG.UNITTEST.SELECTED_TEST_CASES))
        # remove duplicates
        suite_list = Suite.remove_suite_option_duplicates(suite_list)

        # get function name to add to TestCases as filter
        filter_name = inspect.getframeinfo(inspect.currentframe()).function

        # select TestSuites
        for i, case in enumerate(CONFIG.UNITTEST.SELECTED_TEST_CASES):
            tmp = []
            # all TestSuite names
            available_suites = [x['name'] for x in case['suites']]
            # default suite.list
            default_suites = Tools.get_default_suite_list(case)
            if len(default_suites) == 0:
                default_suites = available_suites

            # include TestSuites if True
            include = None
            # check suites
            if suite_list[i] is not None:
                for suite in suite_list[i]:
                    if (suite.startswith('-') and include is True) or (not suite.startswith('-') and include is False):
                        raise TestSuiteOptionsError('Inconsistent TestSuite include options: '
                                                    'TestSuites cannot be included and excluded '
                                                    'for %s TestCase in same time !.'
                                                    % NAME.safe_substitute(name=case['name']))
                    if suite.startswith('-'):
                        include = False
                        # remove minus
                        suite = suite[1:].strip()
                    else:
                        include = True

                    # check suite options
                    if suite not in available_suites:
                        raise TestSuiteNotFoundError('%s TestSuite not found in %s TestCases ! '
                                                     % (NAME.safe_substitute(name=suite),
                                                        NAME.safe_substitute(name=case['name']))
                                                     + 'Use [--suite-list] option to print all available TestSuites.')
                    # include TestSuites
                    if include is True:
                        tmp.append(copy.deepcopy(case['suites'][available_suites.index(suite)]))

                # exclude TestSuites
                if include is False:
                    # remove minus
                    for j in range(len(suite_list[i])):
                        suite_list[i][j] = suite_list[i][j][1:].strip()

                    # add not excluded TestSuites
                    for suite in available_suites:
                        if suite not in suite_list[i]:
                            tmp.append(copy.deepcopy(case['suites'][available_suites.index(suite)]))

                    if len(tmp) == 0:
                        raise TestSuiteOptionsError('All TestSuites cannot be excluded from %s TestCase !'
                                                    % NAME.safe_substitute(name=case['name']))
            else:
                # add default TestSuites
                for suite in default_suites:
                    tmp.append(copy.deepcopy(case['suites'][available_suites.index(suite)]))
            case['suites'] = tuple(tmp)
            # add filter name to list
            case['filters'].append(filter_name)
