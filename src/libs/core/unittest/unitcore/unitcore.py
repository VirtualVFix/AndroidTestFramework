# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

"""
Unittest core module. Function from this module should be replace original unittest functions.
Also run function added new tags to results
"""

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "11/03/17 12:25"

import pytz
from time import time
from config import CONFIG
from ..tools import Tools
from datetime import datetime
from libs.core.logger import getLoggers, LEVEL
from ..config import RESULT_DELIMITER_2, RESULT_NAMES
from libs.core.unittest.config import TEST_TIME_TAG_FORMAT
from libs.core.template import TEST_START, TEST_DONE, NAME


def setUpClass(self):
    """
    Replacement function of original unittest **setUpClass** function
    """
    # add loggers
    self.__logger, self.__syslogger = getLoggers('unittest')

    # call options modules function if registered
    try:
        if hasattr(self, '__libs_options'):
            for opt in self.__libs_options:
                if 'setup_suite' in opt.REGISTERED:
                    self.__syslogger.info('Call setup_suite() of "%s" options module...' % opt.fullname)
                    CONFIG.TEST.CURRENT_STATE = 'setup_suite of "%s" module' % opt.fullname
                    opt.setup_suite()
    except Exception as e:
        self.__syslogger.exception(e)
        raise

    # change state name
    CONFIG.TEST.CURRENT_STATE = "SetUpClass"

    # call original function
    try:
        self.__originalSetUpClass()
    except Exception as e:
        self.__syslogger.exception(e)
        raise


def tearDownClass(self):
    """
    Replacement function of original unittest **tearDownClass** function
    """
    # call options modules function if registered
    try:
        if hasattr(self, '__libs_options'):
            for opt in self.__libs_options:
                if 'teardown_suite' in opt.REGISTERED:
                    self.__syslogger.info('Call teardown_suite() of "%s" options module...' % opt.fullname)
                    CONFIG.TEST.CURRENT_STATE = 'teardown_suite of "%s" module' % opt.fullname
                    opt.teardown_suite()
    except Exception as e:
        self.__syslogger.exception(e)
        raise

    # change state name
    CONFIG.TEST.CURRENT_STATE = "TearDownClass"

    # call original function
    try:
        self.__originalTearDownClass()
    except Exception as e:
        self.__syslogger.exception(e)
        raise


def setUp(self):
    """
    Replacement function of original unittest **setUp** function
    """
    # call options modules function if registered
    try:
        if hasattr(self, '__libs_options'):
            for opt in self.__libs_options:
                if 'setup' in opt.REGISTERED:
                    self.__syslogger.info('Call setup() of "%s" options module...' % opt.fullname)
                    CONFIG.TEST.CURRENT_STATE = 'setup of "%s" module' % opt.fullname
                    opt.setup()
    except Exception as e:
        self.__syslogger.exception(e)
        raise

    # change state name
    CONFIG.TEST.CURRENT_STATE = 'setUp: %s' % self.shortDescription()

    # call original function
    try:
        self.__originalSetUp()
    except Exception as e:
        self.__syslogger.exception(e)
        raise


def tearDown(self):
    """
    Replacement function of original unittest **tearDown** function
    """
    # call options modules function if registered
    try:
        if hasattr(self, '__libs_options'):
            for opt in self.__libs_options:
                if 'teardown' in opt.REGISTERED:
                    self.__syslogger.info('Call teardown() of "%s" options module...' % opt.fullname)
                    CONFIG.TEST.CURRENT_STATE = 'teardown of "%s" module' % opt.fullname
                    opt.teardown()
    except Exception as e:
        self.__syslogger.exception(e)
        raise

    # change state name
    CONFIG.TEST.CURRENT_STATE = "tearDown %s" % self.shortDescription()

    # call original function
    try:
        self.__originalTearDown()
    except Exception as e:
        self.__syslogger.exception(e)
        raise


def run(self, result):
    """
    Replacement function of original unittest **run**.

    Function features:
        - convert Test to subTest loop if required
        - launch Test
        - calculate pass rate
        - collect results to dict

    Result dict structure:

    .. code-block:: python

         {'cycle': CONFIG.TEST.CURRENT_CYCLE,   # Last completed cycle
          'cycles': CONFIG.TEST.TOTAL_CYCLES,   # Total test cycles planed
          'time': spend_time_total,             # Time spend on Test
          'rate': pass_rate,                    # Test pass rate (calculate automatically or may be set in test implementation via **TEST.PASS_RATE** config)
          'result': str_result,                 # String Test result: PASS/FAIL/ERROR/SKIP/NOT RUN
          'errors': errors,                     # Error list
          'fails': fails,                       # Fail list
          'skips': skips,                       # Skip list
          'expected': expected,                 # Expected failure list if @unittest.expectedFailure decorator in use
          'unexpected': unexpected,             # Unexpected success list if @unittest.expectedFailure decorator in use
          'times': times}                       # Spend time list of each cycle when auto cycle feature in use

    Results dict is stored in Test dict as results :func:`src.libs.core.unittest.ScanTests.load_tests`.
    """
    # update current Test name
    CONFIG.TEST.CURRENT_TEST = self._testMethodName

    # interrupt by fail
    if CONFIG.UNITTEST.INTERRUPT_BY_FAIL is True:
        result.failfast = True

    # get current test
    def get_suite_and_test():
        for case in CONFIG.UNITTEST.SELECTED_TEST_CASES:
            for suite in case['suites']:
                for test in suite['tests']:
                    if test['test'] == self and test['index'] == result.testIndex+1:  # testIndex increases after start
                        return suite, test
        # Oops... test not found... oO Why ??? It should not have happened ! Neutrinos mutated ! We are all die !!!!
        raise RuntimeError('Fatality: %s Test not found in selected Tests' % NAME.safe_substitute(name=self.id()))
    current_suite, current_test = get_suite_and_test()

    # test notify
    self.__logger.table('=*', self.__syslogger, level=LEVEL.INFO)
    # self.__logger.table(('NOTIFICATION:', 'c'), self.__syslogger, level=LEVEL.INFO)
    self.__logger.table((CONFIG.UNITTEST.__NOTIFICATION__, 'c'), self.__syslogger, level=LEVEL.INFO)
    self.__logger.table('=*', self.__syslogger, level=LEVEL.INFO)
    # start test
    # self.__logger.newline(self.__syslogger)
    # self.__logger.table('-*', self.__syslogger, level=LEVEL.INFO)
    self.__logger.table((TEST_START.safe_substitute(date=datetime.now(pytz.timezone(CONFIG.SYSTEM.TIMEZONE))
                                                    .strftime(TEST_TIME_TAG_FORMAT),
                                                    name=self._testMethodName,
                                                    second=('/' + current_test['name'])
                                                    if current_test['name'] is not None else '',
                                                    desc=current_test['desc']), 'c'),
                        self.__syslogger, level=LEVEL.INFO)
    self.__logger.table('-*', self.__syslogger)

    # reset local cycles variable
    CONFIG.TEST.CURRENT_CYCLE = 0
    CONFIG.TEST.FAILED_CYCLES = 0
    CONFIG.TEST.PASS_RATE = -1

    # start timer
    start_time = time()

    # get total cycles
    cycles = getattr(self, '%s_cycles' % self._testMethodName.lower(), 0)
    if cycles <= 0 and current_test['name'] is not None:
        cycles = getattr(self, '%s' % Tools.convert_name_to_variable(current_test['name'], 'cycles').lower(), 0)
    CONFIG.TEST.TOTAL_CYCLES = cycles if cycles > 0 else 1

    # run test
    testMethod = None
    except_rate = 100
    pass_total = False
    try:
        testMethod = getattr(self, self._testMethodName)

        # check early skip if test skipped
        if getattr(testMethod, '__unittest_skip__', False):
            # testIndex and testRun must increase each test
            result.testsRun += 1
            result.testIndex += 1
            result.addSkip(self, getattr(testMethod, '__unittest_skip_why__', ''))
        else:
            # get excepted pass rate
            except_rate = getattr(testMethod, '__pass_rate', 0) or getattr(self.__class__, '__pass_rate', 100)
            # get total pass rate cycles according to option
            pass_total = getattr(testMethod, '__rate_by_total_cycles', False) or \
                getattr(self.__class__, '__rate_by_total_cycles', False)

            own_loop = getattr(testMethod, '__own_loop', False) or getattr(self.__class__, '__own_loop', False)
            if own_loop or CONFIG.TEST.TOTAL_CYCLES == 1:
                if own_loop:
                    self.__syslogger.info('Auto Test cycle ignored due to "own_loop" tag found')
                self.__originalRun(result)
            else:
                # convert test to sub test with required test cycles
                def autoTestLoop(self):
                    for i in range(CONFIG.TEST.TOTAL_CYCLES):
                        self.__logger.newline(self.__syslogger)
                        self.__logger.info('Test cycle %d/%d is starting...'
                                           % (CONFIG.TEST.CURRENT_CYCLE+1, CONFIG.TEST.TOTAL_CYCLES))
                        self.__logger.table('%s*' % RESULT_DELIMITER_2, ' *', self.__syslogger, border_delimiter='')
                        cycle_time = time()
                        with self.subTest(msg='Cycle: %d/%d' % (i+1, CONFIG.TEST.TOTAL_CYCLES)):
                            testMethod()

                        spend_time = time() - cycle_time
                        result.addTime(self, spend_time)
                        CONFIG.TEST.CURRENT_CYCLE = i+1

                self.__syslogger.info('Auto Test cycle setup !')
                setattr(self, self._testMethodName, lambda slf=self: autoTestLoop(slf))
                self.__originalRun(result)
    finally:
        if testMethod is not None:
            # restore original Test method
            setattr(self, self._testMethodName, testMethod)

        # Test during
        spend_time_total = float(int((time() - start_time) * 1000)) / 1000

        # collect summary
        errors = [x for x in result.errors if x[0] == result.testIndex]
        fails = [x for x in result.failures if x[0] == result.testIndex]
        skips = [x for x in result.skipped if x[0] == result.testIndex]
        times = [x for x in result.time if x[0] == result.testIndex]
        expected = [x for x in result.expectedFailures if x[0] == result.testIndex]
        unexpected = [x for x in result.unexpectedSuccesses if x[0] == result.testIndex]

        # add current cycles if have only one and test was success
        if sum((len(errors), len(fails), len(skips), len(unexpected))) == 0 and result.testsRun > 0:
            if CONFIG.TEST.CURRENT_CYCLE == 0 and CONFIG.TEST.TOTAL_CYCLES == 1:
                CONFIG.TEST.CURRENT_CYCLE = 1

        # calc pass rate
        pass_rate = CONFIG.TEST.PASS_RATE
        # pass rate not set
        if pass_rate < 0:
            pass_total = CONFIG.TEST.CURRENT_CYCLE if pass_total is False else CONFIG.TEST.TOTAL_CYCLES
            passed = pass_total-(len(errors)+len(fails)+len(unexpected)) - CONFIG.TEST.FAILED_CYCLES
            pass_rate = 0 if result.testsRun == 0 or len(skips) > 0 or passed <= 0 else \
                float(int(float(passed) / CONFIG.TEST.CURRENT_CYCLE * 10000)) / 100 \
                if CONFIG.TEST.CURRENT_CYCLE > 0 else 0

        # string result
        str_result = RESULT_NAMES['pass']
        if len(expected) > 0:
            str_result = RESULT_NAMES['excepted']
        elif len(skips) > 0:
            str_result = RESULT_NAMES['skip']
        elif result.testsRun == 0:
            str_result = RESULT_NAMES['not run']
        elif pass_rate < except_rate:
            if len(errors) > 0:
                str_result = RESULT_NAMES['error']
            elif len(unexpected) > 0:
                str_result = RESULT_NAMES['unexpected']
            else:
                str_result = RESULT_NAMES['fail']

        # pack summary
        current_suite['ran'] = result.testsRun
        summary = {'cycle': CONFIG.TEST.CURRENT_CYCLE,
                   'cycles': CONFIG.TEST.TOTAL_CYCLES,
                   'time': spend_time_total,
                   'rate': pass_rate,
                   'result': str_result,
                   'errors': errors,
                   'fails': fails,
                   'skips': skips,
                   'expected': expected,
                   'unexpected': unexpected,
                   'times': times}
        current_test['results'].append(summary)

        # stop testing by --stop-by-fail if required
        if CONFIG.UNITTEST.INTERRUPT_BY_FAIL is True and str_result in [RESULT_NAMES['fail'], RESULT_NAMES['error'],
                                                                        RESULT_NAMES['unexpected']]:
            # testing should be stopped
            CONFIG.UNITTEST.__SHOULD_STOPPED__ = True
            result.stop()

        # print to console test result
        self.__logger.newline(self.__syslogger)
        self.__logger.table('- *', self.__syslogger, level=LEVEL.INFO)
        self.__logger.table((TEST_DONE.safe_substitute(date=datetime.now(pytz.timezone(CONFIG.SYSTEM.TIMEZONE))
                                                       .strftime(TEST_TIME_TAG_FORMAT),
                                                       result=str_result,
                                                       rate=pass_rate,
                                                       time=(str(spend_time_total) + ' sec') if str_result != 'SKIP'
                                                       else skips[0][2],
                                                       name=self._testMethodName,
                                                       second=('/'+current_test['name'])
                                                       if current_test['name'] is not None else '',
                                                       desc=current_test['desc']), 'c'),
                            self.__syslogger, level=LEVEL.INFO)
        self.__logger.table('- *', self.__syslogger, level=LEVEL.INFO)
        self.__logger.newline(self.__syslogger)
