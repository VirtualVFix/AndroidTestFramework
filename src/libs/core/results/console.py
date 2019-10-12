# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "12/18/2017 4:43 PM"

from config import CONFIG
from libs.core.tools.utility import Utility
from libs.core.template import CASE, NAME, PARAMS
from libs.core.unittest.config import RESULT_NAMES
from libs.core.logger import getLogger, getSysLogger
from .config import CONSOLE_RESULT_TABLE_SIZES as SIZES, EMPTY_RECORD


class Console:
    """
    Print TestCases results to console
    """

    @staticmethod
    def print_results(logger=None, case=None, cycle=None, suite=None):
        """
        Print current TestSuite results to console

        Args:
            logger (logging): Logger to print
            case (dict): TestCase dict
            suite (dict): TestSuite dict
            cycle (int): Current global cycle
        """
        logger = logger or getLogger(__file__)
        syslogger = getSysLogger()
        try:
            for _cycle in range(CONFIG.SYSTEM.TOTAL_CYCLES_GLOBAL):
                if cycle is not None and _cycle != cycle-1:
                    continue

                # TestCases
                for _case in CONFIG.UNITTEST.SELECTED_TEST_CASES:
                    if case is not None and _case != case:
                        continue

                    logger.newline()
                    logger.table('_*', border_delimiter=' ')
                    # logger.table(' ')
                    logger.table(('Results of %s TestCase. Cycle %d/%d'
                                  % (CASE.safe_substitute(case=_case['name'], index=_case['index']),
                                     _cycle+1, CONFIG.SYSTEM.TOTAL_CYCLES_GLOBAL), 'C'))
                    # TestSuites
                    for _suite in _case['suites']:
                        if suite is not None and _suite != suite:
                            continue
                        logger.table(('%s TestSuite %s' % (NAME.safe_substitute(name=_suite['name']),
                                                           'with parameters: %s'
                                                           % PARAMS.safe_substitute(name=_suite['params'])
                                                           if _suite['params'] is not None
                                                           else 'without parameters'), 'C'))
                        logger.table('-*')
                        logger.table(('#', SIZES['number'], 'C'),                         # number
                                     ('Test id'.upper(), SIZES['test_id'], 'C'),          # id
                                     ('Test name'.upper(), SIZES['test_name'], 'C'),      # name
                                     ('Description'.upper(), SIZES['description'], 'C'),  # description
                                     ('Cycles'.upper(), SIZES['cycles'], 'C'),            # cycles
                                     ('Time'.upper(), SIZES['time'], 'C'),                # time
                                     ('Result'.upper(), SIZES['result'], 'C'),            # result
                                     ('Pass Rate'.upper(), SIZES['rate'], 'C'))           # pass rate
                        logger.table('-*')

                        # Tests
                        for t, _test in enumerate(_suite['tests']):
                            _res = _test['results'][_cycle] if _test['results'] is not None and \
                                                               len(_test['results']) > _cycle else None
                            _res_cycle = _res['cycle'] if _res is not None else 0
                            _res_cycles = _res['cycles'] if _res is not None else 0
                            _time = _res['time'] if _res is not None else EMPTY_RECORD
                            if _time != EMPTY_RECORD and _time > 60:
                                _time = Utility.seconds_to_time_format(_time)
                            _result = _res['result'] if _res is not None else RESULT_NAMES['not run']
                            _rate = _res['rate'] if _res is not None else 0
                            logger.table(('%d' % (t+1), SIZES['number'], 'C'),  # number
                                         ('%s' % _test['id'], SIZES['test_id'], 'C'),  # id
                                         ('%s' % (_test['name'] or EMPTY_RECORD), SIZES['test_name'], 'C'),  # name
                                         ('%s' % (_test['desc'] or EMPTY_RECORD), SIZES['description'], 'C'),  # description
                                         (('%d/%d' % (_res_cycle, _res_cycles)) if _res is not None else EMPTY_RECORD,
                                          SIZES['cycles'], 'C'),  # cycles
                                         ('%s' % _time, SIZES['time'], 'C'),  # time
                                         ('%s' % _result, SIZES['result'], 'C'),  # result
                                         ('%.1f %%' % _rate, SIZES['rate'], 'C'))  # pass rate
                        logger.table('-*')
                    logger.newline()
        except Exception as e:
            syslogger.exception(e)
            if CONFIG.SYSTEM.DEBUG:
                raise
            logger.error(e)
