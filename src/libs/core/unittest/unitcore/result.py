# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "12/11/2017 4:26 PM"

from config import CONFIG
from unittest import result
from libs.core.template import TEST_ERROR
from ..config import RESULT_DELIMITER_1, RESULT_DELIMITER_2
from libs.core.logger import getLogger, getSysLogger, LEVEL


class LoggerResult(result.TestResult):
    """
    Custom unittest result class
    """

    def __init__(self, logger=None):
        super(LoggerResult, self).__init__()
        self.logger = logger or getLogger(__file__)
        self.syslogger = getSysLogger()
        self.failfast = False
        self.testIndex = 0
        self.time = []
        self.errors = []
        self.skipped = []
        self.success = []
        self.failures = []
        self.expectedFailures = []
        self.unexpectedSuccesses = []

    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        if doc_first_line:
            return ['%s' % TEST_ERROR.safe_substitute(index=test.testIndex, test=test)] \
                   + [x for x in doc_first_line.split('\n') if x != '']
        else:
            return ['%s' % TEST_ERROR.safe_substitute(index=test.testIndex, test=test)]

    def startTest(self, test):
        self.testIndex += 1
        test.testIndex = self.testIndex
        super(LoggerResult, self).startTest(test)

    def addTime(self, test, time):
        """ Add spent time """
        self.time.append((test, time))

    def addSubTest(self, test, subtest, err):
        # add testIndex to sub test
        if not hasattr(subtest, 'testIndex'):
            subtest.testIndex = self.testIndex

        if err is not None:
            if getattr(self, 'failfast', False):
                self.stop()
            if issubclass(err[0], test.failureException):
                self.addFailure(subtest, err)
            else:
                self.addError(subtest, err)

    def addSuccess(self, test):
        self.success.append((self.testIndex, test))

    def addError(self, test, err):
        # add test index
        if not hasattr(test, 'testIndex'):
            test.testIndex = self.testIndex
        self.errors.append((self.testIndex, test, self._exc_info_to_string(err, test)))
        self.printError('ERROR', test, self.errors)

    def addFailure(self, test, err):
        self.failures.append((self.testIndex, test, self._exc_info_to_string(err, test)))
        self.printError('FAIL', test, self.failures)

    def addSkip(self, test, reason):
        self.skipped.append((self.testIndex, test, reason))
        self.logger.warning('<skipped>', self.syslogger)

    def addExpectedFailure(self, test, err):
        self.expectedFailures.append((self.testIndex, test, self._exc_info_to_string(err, test)))
        self.logger.info('<expected failure>', self.syslogger)

    def addUnexpectedSuccess(self, test):
        self.unexpectedSuccesses.append((self.testIndex, test))
        self.logger.warning('<unexpected success>', self.syslogger)

    def __printErrorViaLogger(self, flavour, level, test, err, inside=True, print_prepare_errors=False):
        """
        Print error using logger. Used in :func:`printError` and :func:`printErrorList` functions.

        Args:
            flavour (str): Error or Fail string
            level (int): Error level
            test ({shortDescription}): Description of test
            err (str): Error traceback
            inside (bool, default True): Use different delimiter. True if error inside test run and False
                if error in total result
            print_prepare_errors (bool, default False): Don't print errors in **setUpClass**
                and **tearDownClass** functions
        """
        # skip prepare errors if required
        if str(test).startswith(('setUpClass', 'tearDownClass')) and not print_prepare_errors :
            return

        # test name
        self.logger.newline(self.syslogger)
        self.logger.table('%s*' % (RESULT_DELIMITER_2 if inside else RESULT_DELIMITER_1), ' *', self.syslogger,
                          border_delimiter='', level=level)
        for i, msg in enumerate(self.getDescription(test)):
            self.logger.table('%s%s' % ((flavour + ': ') if i == 0 else '', msg), self.syslogger,
                              column_delimiter='', level=level)
        # error
        self.logger.table('%s*' % RESULT_DELIMITER_2, ' *', self.syslogger, border_delimiter='', level=level)
        if CONFIG.SYSTEM.DEBUG:
            for e in [x for x in err.split('\n') if x != '']:
                self.logger.table('. %s' % e, self.syslogger, column_delimiter='', level=level)
        else:
            self.logger.table('. %s' % [x for x in err.split('\n') if x != ''][-1], self.syslogger,
                              column_delimiter='', level=level)
            for e in [x for x in err.split('\n') if x != '']:
                self.syslogger.table('. %s' % e, column_delimiter='', level=level)
        self.logger.table('%s*' % RESULT_DELIMITER_2, ' *', self.syslogger, border_delimiter='', level=level)

    def printError(self, flavour, test, errors):
        """ Print error or fail """
        level = LEVEL.ERROR if 'error' in flavour.lower() else LEVEL.WARNING
        for index, _test, err in errors:
            # if test == _test:
            if self.testIndex == index and test == _test and str(test) == str(_test):
                self.__printErrorViaLogger(flavour, level, test, err)
                break

    def printErrors(self):
        self.printErrorList('ERROR', self.errors, print_prepare_errors=True)
        self.printErrorList('FAIL', self.failures)

    def printErrorList(self, flavour, errors, print_prepare_errors=False):
        level = LEVEL.ERROR if 'error' in flavour.lower() else LEVEL.WARNING
        for index, test, err in errors:
            self.__printErrorViaLogger(flavour, level, test, err, inside=False,
                                       print_prepare_errors=print_prepare_errors)
