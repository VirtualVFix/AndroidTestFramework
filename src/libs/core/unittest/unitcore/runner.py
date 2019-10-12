# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "12/12/2017 10:39 AM"

import warnings
from time import time
from .result import LoggerResult
from libs.core.tools import Utility
from ..config import RESULT_DELIMITER_1
from unittest.signals import registerResult
from libs.core.logger import getLogger, getSysLogger


class LoggerRunner:
    """
    Custom unittest Test runner.

    Launch Tests in cycle if required and collect pass rate.
    """

    def __init__(self, logger=None, tb_locals=False, warning=None):
        self.logger = logger or getLogger(__file__)
        self.syslogger = getSysLogger()
        self.result = LoggerResult(logger=logger)
        self.tb_locals = tb_locals
        self.warnings = warning

    def run(self, test):
        """
        Instead of original unittest.TextTestResult may use logger and print errors and fails when it happened
        """
        result = self.result
        registerResult(result)
        # code from original unittest.TextTestRunner class
        with warnings.catch_warnings():
            if self.warnings:
                # if self.warnings is set, use it to filter all the warnings
                warnings.simplefilter(self.warnings)
                # if the filter is 'default' or 'always', special-case the
                # warnings from the deprecated unittest methods to show them
                # no more than once per module, because they can be fairly
                # noisy.  The -Wd and -Wa flags can be used to bypass this
                # only when self.warnings is None.
                if self.warnings in ['default', 'always']:
                    warnings.filterwarnings('module', category=DeprecationWarning,
                                            message=r'Please use assert\w+ instead.')
            start_time = time()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()
            try:
                test(result)
            finally:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()
        # end of code from original unittest.TextTestRunner class
        time_taken = time() - start_time
        # print fail/error results
        result.printErrors()
        msg = ['Ran %d test%s%s' % (result.testsRun, result.testsRun != 1 and "s" or "",
                                    ('. Taken time: %s' % Utility.seconds_to_time_format(time_taken)
                                     if time_taken > 60 else (' in %.3fs' % time_taken)))]
        self.logger.table('%s*' % RESULT_DELIMITER_1, ' *', self.syslogger, border_delimiter='')

        # made result list
        failed, errored = len(result.failures), len(result.errors)
        if failed:
            msg.append("failures=%d" % failed)
        if errored:
            msg.append("errors=%d" % errored)
        unexpectedSuccesses = len(result.unexpectedSuccesses)
        expectedFails, skipped = len(result.expectedFailures), len(result.skipped)
        if skipped:
            msg.append("skipped=%d" % skipped)
        if expectedFails:
            msg.append("expected failures=%d" % expectedFails)
        if unexpectedSuccesses:
            msg.append("unexpected successes=%d" % unexpectedSuccesses)

        self.logger.info('%s%s' % (msg[0], (' (%s)' % ', '.join(msg[1:])) if len(msg) > 1 else ''), self.syslogger)
        self.logger.newline(self.syslogger)

        return result
