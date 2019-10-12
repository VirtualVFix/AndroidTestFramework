# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "11/01/17 12:30"

import re
import inspect
from config import CONFIG
from unittest import defaultTestLoader
from libs.core.unittest.wait import Wait
from libs.core.template import NAME, SUITE_FULL
from libs.core.logger import getLogger, getSysLogger
from libs.core.unittest.unitcore import run, setUp, tearDown, setUpClass, tearDownClass


class ScanTests:
    """ Scan TestSuites to find unittests functions """

    def __init__(self, logger=None):
        self.logger = logger or getLogger(__file__)
        self.syslogger = getSysLogger()

    async def load_tests(self, libs_options):
        """
        Load all available Tests for selected TestSuites and update CONFIG.UNITTEST.SELECTED_TEST_CASES list.

        All tests packaging to **suites['tests']** list for each TestCase

        Tests loading via :func:`defaultTestLoader.loadTestsFromTestCase()`
        Also all unittest function like setUp, tearDown, etc. replaced with analog from
        :mod:`src.libs.core.unittest.unitcore` module.

        Tests packaging to dict with following structure:

        .. code-block:: python

            {'id': 'TestId',                # Function name returns by id() unittest function
             'name': 'ShortDescription',    # Test description before '|' symbol returns by shortDescription() unittest function or None
             'desc': 'FullDescription',     # Test description after '|' symbol returns by shortDescription() unittest function or None
             'index': int,                  # Test index to identify duplicate Tests. Starting from 1
             'results': [],                 # List of results dictionaries for each global cycles. Empty before Test run
             'test': 'Function'}            # Test function link to launch

        Function add TestCase filter.

        Filters:
            load_tests: When Tests were loaded

        Details of **results** structure may be found in :func:`unitcore.run` function.
        Test package stored in TestSuite list for each TestCase :func:`ScanCases.generate_cases_dict`.
        """
        # wait for selected suites
        await Wait.wait_for_selected_suites()

        # get function name to add to filter tags
        filter_name = inspect.getframeinfo(inspect.currentframe()).function

        # scan all cases
        for case in CONFIG.UNITTEST.SELECTED_TEST_CASES:
            # scan all suites
            for suite in case['suites']:
                result = []
                cls = suite['class']
                # add libs options
                if not hasattr(cls, '__libs_options'):
                    setattr(cls, '__libs_options', libs_options)

                # replace unittest functions in Test class
                if not hasattr(cls, '__originalSetUpClass'):
                    setattr(cls, '__originalSetUpClass', cls.setUpClass)
                    cls.setUpClass = lambda slf=cls: setUpClass(slf)
                if not hasattr(cls, '__originalTearDownClass'):
                    setattr(cls, '__originalTearDownClass', cls.tearDownClass)
                    cls.tearDownClass = lambda slf=cls: tearDownClass(slf)
                if not hasattr(cls, '__originalSetUp'):
                    setattr(cls, '__originalSetUp', cls.setUp)
                    cls.setUp = lambda slf=cls: setUp(slf)
                if not hasattr(cls, '__originalTearDown'):
                    setattr(cls, '__originalTearDown', cls.tearDown)
                    cls.tearDown = lambda slf=cls: tearDown(slf)
                if not hasattr(cls, '__originalRun'):
                    setattr(cls, '__originalRun', cls.run)
                    cls.run = lambda slf=cls, *args, **kwargs: run(slf, *args, **kwargs)

                # keep default values
                # self.syslogger.info('Checking default values of [%s] class for [%s.%s] TestSuite ...'
                #                     % (cls.__name__, case['name'], suite['name']))
                # await self.check_default_values(cls)
                # self.syslogger.done()

                # get tests from class
                self.syslogger.info('Loading Tests for %s TestSuite' % SUITE_FULL.safe_substitute(case=case['name'],
                                                                                                  suite=suite['name'],
                                                                                                  index=case['index']))
                test_list = defaultTestLoader.loadTestsFromTestCase(suite['class'])
                for test in test_list._tests:
                    desc = test.shortDescription()
                    tid = test.id().split('.')[-1]
                    # add test to TestSuite
                    result.append({'id': tid.lower(),
                                   'name': desc.split('|')[0].strip('-').strip().lower() if desc is not None else None,
                                   'desc': desc.split('|')[1].strip() if desc is not None and desc.find('|') > -1 else desc,
                                   'index': -1,
                                   'results': [],
                                   'test': test})
                    self.syslogger.info('Found %s/%s <%s> Test' % (NAME.safe_substitute(name=tid),
                                                                   NAME.safe_substitute(name=result[-1]['name']),
                                                                   result[-1]['desc']))
                # add tests sorted by digits in test ID
                suite['tests'] = sorted(result, key=lambda data: [int(x) if x.isdigit() else x
                                                                  for x in re.split('(\d+)', data['id'])])
                # update test index after sort
                for i, test in enumerate(suite['tests']):
                    test['index'] = i+1

                # add auto-variables
                # ScanTests.create_auto_variables(cls, result)
                self.syslogger.done()

            # add filter to case
            case['filters'].append(filter_name)

    # @staticmethod
    # def create_auto_variables(cls, tests):
    #     """
    #     Create auto-variables like testXX_cycles/NAME_cycles
    #
    #     Args:
    #          cls (class): Class to add variables
    #          tests (list): List of Test dists
    #     """
    #     for test in tests:
    #         # create XX_cycles variables
    #         cycle_id = '%s_cycles' % test['id']
    #         value = getattr(cls, cycle_id, 0)
    #         if test['name'] is not None:
    #             cycle_name = '%s_cycles' % Tools.convert_name_to_variable(test['name']).lower()
    #             value = value or getattr(cls, cycle_name, 1)
    #             setattr(cls, cycle_name, value)
    #         setattr(cls, cycle_id, value or 1)


    # @staticmethod
    # async def check_default_values(cls):
    #     """
    #     Check default variables in class and restore static values to default if found or keep current static
    #     values to default variables if not.
    #     """
    #     # get all variables
    #     variables = ([x for x in cls.__dict__ if not x.startswith('_')
    #                   and not hasattr(cls.__dict__[x], '__call__')
    #                   and not hasattr(cls.__dict__[x], '__func__')])
    #     # scan all variables
    #     for var in variables:
    #         default = '_%s__default__%s' % (cls.__name__, var)
    #         # set to default value
    #         if hasattr(cls, default):
    #             print('HAVE: ', default)
    #             setattr(cls, var, getattr(cls, default))
    #         # store default values
    #         else:
    #             print('SET: ', default)
    #             setattr(cls, default, getattr(cls, var))
