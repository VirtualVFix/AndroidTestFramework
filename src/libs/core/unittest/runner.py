# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "11/01/17 12:31"

import sys
from time import time
from config import CONFIG
from ..results import Console
from unittest import TestSuite
from .config import RESULT_NAMES
from libs.core.logger import getLoggers
from .unitcore.runner import LoggerRunner
from libs.core.tools import Utility, Async
from libs.core.template import NAME, SUITE_FULL, TEST_ERROR, PARAMS
from ..exceptions import InterruptByUser, InterruptByError, InterruptByFail


class Runner:
    """
    Launch tests
    """

    def __init__(self, libs_options):
        """
        Args:
             libs_options (list): Libs Options list with setup functions
        """
        self.libs_options = libs_options
        self.logger, self.syslogger = getLoggers(__file__)

    def run_suite(self, case, suite):
        """
        Launch Test from TestSuite

        Args:
            case (dict): Current TestCase
            suite (dict): Current TestSuite
        """
        try:
            if not getattr(CONFIG.UNITTEST, '__SHOULD_STOPPED__', False):
                test_suit = TestSuite()
                for test in suite['tests']:
                    test_suit.addTest(test['test'])
                # launch TestSuite
                result = LoggerRunner(logger=None).run(test_suit)
                # check errors during test prepare
                if len(result.errors) > 0:
                    for err in result.errors:
                        if str(err[1]).startswith(('setUpClass', 'tearDownClass')):
                            # add errors to TestSuite
                            if 'errors' in suite:
                                suite['errors'].append(err)
                            else:
                                suite['errors'] = [err]
        except KeyboardInterrupt:
            raise
        except Exception as e:
            # self.syslogger.exception(e)
            self.logger.error('Error of performing %s TestSite %s: %s'
                              % (SUITE_FULL.safe_substitute(case=case['name'], suite=suite['name'], index=case['index']),
                                 ('with parameters: %s' % PARAMS.safe_substitute(name=suite['params'])
                                 if suite['params'] is not None else 'without parameters'), e))
            raise
        finally:
            # Close eventLoop for each TestSuite
            Async.close_loop()

    def _setup_suite(self):
        """ execute all "setup_suite" function from libs options """
        for opt in self.libs_options:
            if 'setup_suite' in opt.REGISTERED:
                self.syslogger.info('Execute "setup_suite" of %s options module...'
                                    % NAME.safe_substitute(name=opt.fullname))
                opt.setup_suite()
                self.syslogger.done()

    def _teardown_suite(self):
        """ execute all "teardown_suite" function from libs options """
        for opt in self.libs_options:
            if 'teardown_suite' in opt.REGISTERED:
                self.syslogger.info('Execute "teardown_suite" of %s options module...'
                                    % NAME.safe_substitute(name=opt.fullname))
                opt.teardown_suite()
                self.syslogger.done()

    def launch(self):
        """
        Launch all tests from **CONFIG.UNITTEST.SELECTED_TEST_CASES**
        """
        # global TestCase cycle
        start_time = time()
        CONFIG.UNITTEST.__LAST_ERROR__ = None
        try:
            for cycle in range(CONFIG.SYSTEM.TOTAL_CYCLES_GLOBAL):
                CONFIG.SYSTEM.CURRENT_CYCLE_GLOBAL = cycle+1
                self.logger.newline(self.syslogger)
                if CONFIG.SYSTEM.TOTAL_CYCLES_GLOBAL > 1:
                    self.logger.table(': *', ('CYCLE %d/%d' % (CONFIG.SYSTEM.CURRENT_CYCLE_GLOBAL,
                                                               CONFIG.SYSTEM.TOTAL_CYCLES_GLOBAL), 15, 'C'), ': *',
                                      self.syslogger, border_delimiter=' ')
                    self.logger.newline(self.syslogger)
                self.logger.info('ARGUMENTS: %s %s' % (sys.argv[0], CONFIG.UNITTEST.__USED_OPTIONS__))

                # TestCases
                for i, case in enumerate(CONFIG.UNITTEST.SELECTED_TEST_CASES):
                    # update current TestCase and TestCase index
                    CONFIG.TEST.CURRENT_CASE = case['name']
                    CONFIG.TEST.CURRENT_CASE_INDEX = i+1

                    # TestSuites
                    for suite in case['suites']:
                        self.logger.newline(self.syslogger, lines=1)
                        # self.logger.table('-*', self.syslogger, border_delimiter='-')
                        # update current_suite
                        CONFIG.TEST.CURRENT_SUITE = suite['name']
                        # Add TestSuite notify
                        CONFIG.UNITTEST.__NOTIFICATION__ = '%s TestSuite ' \
                                                           % SUITE_FULL.safe_substitute(case=case['name'],
                                                                                        index=case['index'],
                                                                                        suite=suite['name'])
                        CONFIG.UNITTEST.__NOTIFICATION__ += ('with parameters: %s' %
                                                         PARAMS.safe_substitute(name=suite['params'])) \
                            if suite['params'] is not None else 'without parameters'
                        CONFIG.UNITTEST.__NOTIFICATION__ += ('| [%s][%s_%s] ' % (CONFIG.DEVICE.DEVICE_NAME,
                                                                                 CONFIG.DEVICE.BUILD_TYPE,
                                                                                 CONFIG.DEVICE.BUILD_VERSION)) \
                            if CONFIG.DEVICE.DEVICE_NAME != '' else ''
                        CONFIG.UNITTEST.__NOTIFICATION__ += ' | Cycle: %d/%d ' % (CONFIG.SYSTEM.CURRENT_CYCLE_GLOBAL,
                                                                                  CONFIG.SYSTEM.TOTAL_CYCLES_GLOBAL)
                        # Run TestSuite
                        try:
                            try:
                                self._setup_suite()
                                self.run_suite(case=case, suite=suite)
                                self._teardown_suite()
                            finally:
                                # print results after suite
                                # print results if we have more than one test case or test suite
                                if not (len(CONFIG.UNITTEST.SELECTED_TEST_CASES) == 1 and len(case['suites']) == 1):
                                    Console.print_results(logger=self.logger, case=case, cycle=cycle+1, suite=suite)
                                if CONFIG.UNITTEST.INTERRUPT_BY_FAIL:
                                    for c in CONFIG.UNITTEST.SELECTED_TEST_CASES:
                                        for s in c['suites']:
                                            msg = '%s TestSuite %s' % (SUITE_FULL.safe_substitute(case=case['name'],
                                                                                                  suite=suite['name'],
                                                                                                  index=case['index']),
                                                                       ('with parameters: %s'
                                                                        % PARAMS.safe_substitute(name=suite['params'])
                                                                       if suite['params'] is not None
                                                                       else 'without parameters'))
                                            for e in s['tests']:
                                                if e['results'] is None or len(e['results']) <= cycle:
                                                    continue
                                                if e['results'][cycle]['result'] == RESULT_NAMES['error']:
                                                    err = e['results'][cycle]['errors'][0]
                                                    raise InterruptByError('Error of performing "%s" Test of %s:\n%s'
                                                                           % (TEST_ERROR.safe_substitute(index=err[0],
                                                                                                         test=err[1]),
                                                                              msg, err[2]))
                                                elif e['results'][cycle]['result'] == RESULT_NAMES['fail']:
                                                    fail = e['results'][cycle]['fails'][0]
                                                    raise InterruptByFail('Error of performing "%s" Test of %s:\n%s'
                                                                          % (TEST_ERROR.safe_substitute(index=fail[0],
                                                                                                        test=fail[1]),
                                                                             msg, fail[2]))
                        except KeyboardInterrupt as e:
                            self.syslogger.exception(e)
                            self.logger.warning('Performing of %s TestSuite was interrupted by User !'
                                                % (SUITE_FULL.safe_substitute(case=case['name'], index=case['index'],
                                                                              suite=suite['name'])))
                            raise InterruptByUser(e)
                        except Exception as e:
                            self.syslogger.exception(e)
                            if CONFIG.SYSTEM.DEBUG:
                                self.logger.exception(e)
                            # keep last error with traceback
                            CONFIG.UNITTEST.__LAST_ERROR__ = sys.exc_info()
                            raise
                        finally:
                            CONFIG.UNITTEST.__NOTIFICATION__ = ''
        finally:
            # print final result
            self.logger.newline(self.syslogger, lines=1)
            self.logger.table('-*', self.syslogger)
            self.logger.table('>  *', ('Results summary'.upper(), 15, 'c'), '<  *', column_delimiter=' ',
                              border_delimiter=' ')
            self.logger.table('-*', self.syslogger)
            Console.print_results(logger=self.logger)
            spend_time = time()-start_time
            self.logger.info('Total time: %s' % (Utility.seconds_to_time_format(spend_time)
                                                 if spend_time > 60 else '%.3fs' % spend_time))
            self.logger.newline()
            # complete info
            if CONFIG.DEVICE.DEVICE_NAME:
                self.logger.info('[%s][%s_%s] ' % (CONFIG.DEVICE.DEVICE_NAME, CONFIG.DEVICE.BUILD_TYPE,
                                                   CONFIG.DEVICE.BUILD_VERSION))
            self.logger.info('Used options: '.upper() + CONFIG.UNITTEST.__USED_OPTIONS__)
            # logs dir
            _logs = CONFIG.SYSTEM.LOG_PATH
            if _logs is None:
                from libs.core.logger.config import LOCAL
                _logs = LOCAL.DEFAULT_LOGS_FOLDER
            self.logger.info('Logs folder: %s' % _logs)
            self.logger.newline()
            # print warnings
            for x in CONFIG.SYSTEM.WARNINGS:
                self.logger.warning(x, self.syslogger)
            if len(CONFIG.SYSTEM.WARNINGS) > 0:
                self.logger.newline(self.syslogger)
