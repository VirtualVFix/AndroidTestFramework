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
from libs.core.results.config import HTML_RESULT_TABLE_SIZES as SIZES, EMPTY_RECORD, HTML_COLOR_FAIL
from libs.core.results.config import HTML_COLOR_LINE1, HTML_COLOR_LINE2, HTML_COLOR_PASS, HTML_COLOR_SKIP
from libs.core.results.config import HTML_COLOR_HEAD, HTML_COLOR_HEAD1, HTML_COLOR_HEAD2, HTML_COLOR_ERROR


class Html:
    """
    Print TestCases results to console
    """

    @staticmethod
    def __format_error(errors, color_head, color_error):
        """
        Format error to HTML format

        Args:
            errors (list): List of errors
        """
        results = ''
        for j, _err in enumerate(errors):
            if CONFIG.SYSTEM.DEBUG:
                _text = []
                for x in [x for x in _err[2].split('\n') if x != '']:
                    counter = 0
                    for i in range(len(x)):
                        if x[i] == ' ':
                            counter += 1
                        else:
                            break
                    _text.append('&nbsp' * (counter * 2) + x.strip())
                _text = str(_err[1]) + '<br>' + '<br>'.join(_text)
            else:
                _text = [x for x in _err[2].split('\n') if x != '']
                _text = str(_err[1]) + '<br>' + _text[0] + '<br>' + _text[-1]

            if j < len(errors) - 1:
                _text += '<br>-'

            results += '<tr><td style="text-align: left;"'
            results += ' colspan="%d" bgcolor="%s" width="100%%">' \
                       % (len(SIZES), color_head)
            results += '<font color="%s">%s</font></td></tr>' \
                       % (color_error, _text)
        return results

    @staticmethod
    def print_results(logger=None, case=None, cycle=None, suite=None, fail_traceback=False):
        """
        Send result to email

        Args:
            logger (logging): Logger to print
            case (dict): TestCase dict
            suite (dict): TestSuite dict
            cycle (int): Current global cycle
            fail_traceback (bool): Add failed test traceback
        """
        logger = logger or getLogger(__file__)
        syslogger = getSysLogger()

        results = '<html><head><style type="text/css">td{word-wrap: break-word; text-align: center}; '
        results += 'th{word-wrap: break-word; text-align: center}</style></head>'
        results += '<br><table border="0" width="100%" cellspacing="0">'
        try:
            for _cycle in range(CONFIG.SYSTEM.TOTAL_CYCLES_GLOBAL):
                if cycle is not None and _cycle != cycle-1:
                    continue

                # TestCases
                for _case in CONFIG.UNITTEST.SELECTED_TEST_CASES:
                    if case is not None and _case != case:
                        continue

                    results += '<tr><th bgcolor="%s" colspan="%d" width="100%%"><b>' % (HTML_COLOR_HEAD, len(SIZES))
                    results += 'Results of %s TestCase. Cycle %d/%d' \
                               % (CASE.safe_substitute(case=_case['name'], index=_case['index']), _cycle+1,
                                  CONFIG.SYSTEM.TOTAL_CYCLES_GLOBAL)
                    results += '</b></th></tr>'

                    # TestSuites
                    for _suite in _case['suites']:
                        if suite is not None and _suite != suite:
                            continue

                        results += '<tr><th bgcolor="%s" colspan="%d" width="100%%">' % (HTML_COLOR_HEAD, len(SIZES))
                        results += '%s TestSuite %s' % (NAME.safe_substitute(name=_suite['name']),
                                                        'with parameters: %s'
                                                        % PARAMS.safe_substitute(name=_suite['params'])
                                                        if _suite['params'] is not None
                                                        else 'without parameters')
                        results += '</th></tr>'

                        # generate table header
                        results += '<tr>'
                        for i, (text, size) in enumerate([
                            # number
                            ('No', SIZES['number']),
                            # id
                            ('Test id', SIZES['test_id']),
                            # name
                            ('Test name', SIZES['test_name']),
                            # description
                            ('Description', SIZES['description']),
                            # cycles
                            ('Cycles', SIZES['cycles']),
                            # time
                            ('Time', SIZES['time']),
                            # result
                            ('Result', SIZES['result']),
                            # pass rate
                            ('Pass Rate', SIZES['rate'])
                        ]):
                            results += '<th bgcolor="%s" width="%d%%"><b>%s</b></th>' \
                                       % (HTML_COLOR_HEAD2 if i % 2 == 0 else HTML_COLOR_HEAD1, size, text.upper())
                        results += '</tr>'

                        # generate test results
                        results += '<tr>'
                        for t, _test in enumerate(_suite['tests']):
                            # test results
                            _res = _test['results'][_cycle] if _test['results'] is not None and \
                                                               len(_test['results']) > _cycle else None
                            # test executed cycles
                            _res_cycle = _res['cycle'] if _res is not None else 0
                            # test total cycles
                            _res_cycles = _res['cycles'] if _res is not None else 0
                            # test execution time
                            _time = _res['time'] if _res is not None else EMPTY_RECORD
                            if _time != EMPTY_RECORD and _time > 60:
                                _time = Utility.seconds_to_time_format(_time)
                            # test result
                            _result = _res['result'] if _res is not None else RESULT_NAMES['not run']
                            # test pass rate
                            _rate = _res['rate'] if _res is not None else 0
                            # errors traceback
                            _errors = None if _res is None else _res['errors'] if len(_res['errors']) > 0 else None
                            # fail traceback
                            if _errors is None:
                                _errors = None if not fail_traceback else None if _res is None else _res['fails'] \
                                    if len(_res['fails']) > 0 else _res['unexpected'] \
                                    if len(_res['unexpected']) > 0 else None

                            # generate results lines
                            for i, (text, size) in enumerate([
                                # number
                                (t+1, SIZES['number']),
                                # id
                                (_test['id'], SIZES['test_id']),
                                # name
                                ('%s' % (_test['name'] or EMPTY_RECORD), SIZES['test_name']),
                                # description
                                ('%s' % (_test['desc'] or EMPTY_RECORD), SIZES['description']),
                                # cycles
                                (('%d/%d' % (_res_cycle, _res_cycles)) if _res is not None else EMPTY_RECORD,
                                 SIZES['cycles']),
                                # time
                                (_time, SIZES['time']),
                            ]):
                                results += '<td bgcolor="%s" width="%d%%">%s</td>' \
                                           % (HTML_COLOR_LINE2 if i % 2 == 0 else HTML_COLOR_LINE1, size, text)

                            # add test result
                            results += '<td bgcolor="%s" width="%d%%"><b><font color="%s">%s</font></b></td>' \
                                       % (HTML_COLOR_LINE2, SIZES['result'], HTML_COLOR_PASS
                                          if _result.lower() in ['pass', 'excepted']
                                          else HTML_COLOR_SKIP if _result.lower() in ['skip', 'not run']
                                          else HTML_COLOR_FAIL, _result.upper())
                            # add test pass rate
                            results += '<td bgcolor="%s" width="%d%%"><b><font color="%s">%s%%</font></b></td>' \
                                       % (HTML_COLOR_LINE1, SIZES['result'], HTML_COLOR_PASS
                                          if _result.lower() in ['pass', 'excepted']
                                          else HTML_COLOR_SKIP if _result.lower() in ['skip', 'not run']
                                          else HTML_COLOR_FAIL, _rate)
                            results += '</tr>'

                            # add errors or fail traceback if available
                            if _errors is not None:
                                results += Html.__format_error(_errors, HTML_COLOR_HEAD1, HTML_COLOR_ERROR)

                        # add TestSuite errors
                        if 'errors' in _suite:
                            results += '<tr><th style="text-align: center;"'
                            results += 'bgcolor="%s" colspan="%d" width="100%%"><b><font color="%s">' \
                                       % (HTML_COLOR_HEAD, len(SIZES), HTML_COLOR_ERROR)
                            results += 'Test Suite error'.upper()
                            results += '</font></b></th></tr>'
                            results += Html.__format_error(_suite['errors'], HTML_COLOR_HEAD1, HTML_COLOR_ERROR)
        except Exception as e:
            syslogger.exception(e)
            if CONFIG.SYSTEM.DEBUG:
                raise
            logger.error(e)
        finally:
            # Framework error
            if CONFIG.UNITTEST.__LAST_ERROR__ is not None:
                import traceback
                if CONFIG.SYSTEM.DEBUG:
                    _text = []
                    for x in [x for x in ''.join(traceback.TracebackException(*CONFIG.UNITTEST.__LAST_ERROR__,
                                                                              limit=None)
                                                           .format(chain=True)).split('\n') if x.strip() != '']:
                        counter = 0
                        for i in range(len(x)):
                            if x[i] == ' ':
                                counter += 1
                            else:
                                break
                        _text.append('&nbsp' * (counter * 2) + x.strip())
                    _text = '<br>'.join(_text)
                else:
                    _text = [x for x in ''.join(traceback.TracebackException(*CONFIG.UNITTEST.__LAST_ERROR__,
                                                                             limit=0)
                                                          .format(chain=True)).split('\n') if x.strip() != '']
                    _text = '<br>'.join(_text)

                results += '<tr height="5"></tr><tr><th style="text-align: center;"'
                results += 'bgcolor="%s" colspan="%d" width="100%%"><b><font color="%s">' \
                           % (HTML_COLOR_HEAD, len(SIZES), HTML_COLOR_ERROR)
                results += 'Framework error'.upper()
                results += '</font></b></th></tr>'
                results += '<tr><td style="text-align: left;" colspan="%d" bgcolor="%s" width="100%%">' \
                           % (len(SIZES), HTML_COLOR_HEAD1)
                results += '<font color="%s">%s</font></td></tr>' % (HTML_COLOR_ERROR, _text)

            results += '<tr><th bgcolor="%s" colspan="%s" width="100%%" height="1px"></th></tr>' \
                       % (HTML_COLOR_HEAD, len(SIZES))
            results += '</table></html>'
        return results
