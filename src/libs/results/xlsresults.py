# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/23/18 12:53"

import os
import locale
from xlwt import Workbook, easyxf
from libs.core.logger import getLoggers
from libs.results.base.exceptions import ResultsError
from libs.results.base.constants import USE_POINT_AS_DECIMAL_SYMBOL


class XLSResult(object):
    """ Adds results into Excel doc """

    def __init__(self, sheet_name, file_name):
        self.logger, self.syslogger = getLoggers(__file__)

        # xls spreadsheet
        self._book = Workbook()
        # spreadsheet sheet
        self._sheet = self._book.add_sheet(sheet_name, cell_overwrite_ok=True)

        assert file_name.endswith('.xls'), 'File name error: Spreadsheet support ".xls" files only !'
        self._file_name = file_name

        self._results = [[]]  # result for all runs
        self._results_field = []  # result fields

        # row and col in spreadsheet
        self.__cycle_names = [None]  # cycles names
        self.__current_row = 1
        self.__test_row = 1
        self.__current_col = 1
        self.__name_row = 1
        self.__best_row = 1
        self.__current_cycle = 0  # result cycle
        self.__already_saved = -1  # counter of results added to spreadsheet

        # cell styles
        self.style_value = easyxf('align: horiz center')
        self.style_bold = easyxf('font: bold on; align: horiz left')
        self.style_header = easyxf('font: bold on; align: wrap on, vert centre, horiz center')
        self.style_fail = easyxf('font: bold on, color red; align: wrap on, vert centre, horiz left')

        # add column description
        self._sheet.write(0, 0, 'Test Name', self.style_header)
        self._sheet.write(0, 1, 'Results', self.style_header)

        # save results in google sheet format [Benchmark name, (field1, value1), ()...]
        self.gsheet_results = []

    def _replaceDecimal(self, value, point_decimal=True):
        if value is None: return None  # return ''
        _value = str(value).replace(',', '.').strip()
        if '.' in _value:
            try:
                locale.setlocale(locale.LC_ALL, '')
                _dec = locale.localeconv()['decimal_point']
                return float(_value) if _dec == '.' or not point_decimal else _value
            except:
                return _value
        else:
            try:
                return int(_value)
            except:
                return _value

    def save(self):
        """ save results """
        try:
            self._book.save(self._file_name)
        except Exception as e:
            self.syslogger.exception(e)
            i = 1
            while True:
                newfile = '{}_({}).xls'.format(self._file_name[:-4], i)
                if not os.path.exists(newfile):
                    self.logger.warn('Save results error. Perhaps the file is in use by another process. '
                                     'Results will saved to %s file.' % newfile)
                    self._book.save(newfile)
                    self._file_name = newfile
                    return

    def new_test(self, name, style=None):
        """ create new test in results """
        self.__test_row = max(self.__current_row, self.__name_row, self.__best_row)
        self.__name_row = self.__test_row
        self.__best_row = self.__test_row
        self.__current_row = self.__test_row
        self.__current_cycle = 0
        self.__current_col = 1
        self.__cycle_names = [None]  # clear cycles names
        self.__already_saved = -1  # counter of results added to spreadsheet
        self._results = [[]]  # result for all runs
        self._results_field = []  # result fields
        self.__add_name(name, self.style_header if style is None else style)
        self.gsheet_results = [name]  # results in google sheet format

    def new_cycle(self, name=None, rename_only=False):
        """
        Create new cycle

        Args:
            name (str, default None): Name of cycle. Will be "Cycles Digit" if None
            rename_only (bool, default False): Rename current cycles without add new
        """
        if not rename_only:
            self.__current_cycle += 1
            self.__current_col += 1
            self._results.append([])
            self.__cycle_names.append(name)
        else:
            self.__cycle_names[self.__current_cycle] = name
    #        self.gsheet_results = self.gsheet_results[1:] # clear results in google sheet format

    def add_name(self, field):
        """ add test field """
        if self.__current_cycle == 0:
            self._results_field.append(str(field).strip())

    def add_result(self, value):
        """ add test result """
        self._results[self.__current_cycle].append(self._replaceDecimal(value))

    def failed_test(self, name, msg):
        self.__best_row = self.__name_row
        self.__add_name(name, style=self.style_fail)
        self.__add_best(msg, style=self.style_fail)

    def __add_name(self, name, style=None):
        if style:
            self._sheet.write(self.__name_row, 0, str(name), style)
        else:
            self._sheet.write(self.__name_row, 0, str(name))
        self.__name_row += 1

    def __add_best(self, value, style=None):
        self._sheet.write(self.__best_row, 1, self._replaceDecimal(value, point_decimal=USE_POINT_AS_DECIMAL_SYMBOL),
                          self.style_value if style is None else style)
        self.__best_row += 1

    def __add_current(self, value, cycle=0, style=None):
        if cycle > 0:
            self.__current_row = self.__test_row
            self.__current_col = cycle + 1
        self._sheet.write(self.__current_row, self.__current_col,
                          self._replaceDecimal(value, point_decimal=USE_POINT_AS_DECIMAL_SYMBOL),
                          self.style_value if style is None else style)
        self.__current_row += 1

    def __sort_results(self, order_list=None):
        """ sorted results """
        if not order_list is None:
            _result = [[] for x in range(len(self._results))]
            for i in range(len(self._results)):
                for j in range(len(order_list)):
                    if order_list[j] in self._results_field:
                        if len(self._results[i]) == 0:
                            _result[i] = []
                            break
                        _result[i].append(self._results[i][self._results_field.index(order_list[j])]
                                          if self._results_field.index(order_list[j]) < len(self._results[i]) else '')
                    else:
                        raise ResultsError('Results sorted error: Order field [%s] is not found in results.'
                                           % order_list[j])
            return order_list, _result
        return self._results_field, self._results

    def collect_results(self, summary_type='best', average_list=None, order_list=None):
        """ collection results
            summary type: ['best', 'average', 'best_and_average']
            if summary type == 'best_and_average' you should specified 'average' fields in average_list.
        """
        # logging raw results
        self.syslogger.info('RAW benchmark results: {}, {}'.format(self._results_field, self._results))
        try:
            for x in zip(self._results_field, *self._results):
                self.syslogger.info('RAW: {}'.format(x))
        except:
            pass

        if order_list is not None:
            assert (len(order_list) == len(set(order_list))) and None not in order_list \
                   and isinstance(order_list, list), 'Order list should not contain duplicates and None value !'
        assert summary_type in ['best', 'average', 'best_and_average', 'none'], \
            'Summary type "{}" doesn\'t supported. ' \
            'Supports the following values: "best", "average", "best_and_average" or "None" !'.format(summary_type)

        if summary_type == 'best_and_average':
            assert not average_list is None and len(average_list) > 0 and isinstance(average_list, list), \
                'You should specify "average list" for "best_and_average" summary type !'
        try:
            # sort results
            _fields, _results = self.__sort_results(order_list)

            # write all results to spreadsheet
            def add_results(index):
                # add cycles
                if len(_results) > 1:
                    # add cycles name
                    self.__add_current(('Cycle %d' % (index + 1)) if index >= len(self.__cycle_names)
                                                                     or self.__cycle_names[index] is None
                                       else self.__cycle_names[index],
                                       index + 1, self.style_header)
                else:
                    self.__add_current('')
                # add values
                for j in range(len(_fields)):
                    _exists = True if j < len(_results[index]) else False
                    self.__add_current(_results[index][j] if _exists else '',
                                       style=self.style_fail if _exists and isinstance(_results[index][j], str)
                                                                and 'fail' in _results[index][j].lower()
                                       else self.style_value)

            # write results to spreadsheet
            for i in range(len(_results)):
                if i <= self.__already_saved: continue
                if i == 0:
                    # add fields
                    for j in range(len(_fields)):
                        self.__add_name(_fields[j])

                # add cycles and values
                if self.__already_saved == 0:
                    add_results(i-1)
                add_results(i)
                self.__already_saved = i

            # summary results
            if len(_results) > 1:
                self.__best_row = self.__test_row
                self.__add_best('')
                for j in range(len(_fields)):
                    _list = [x[j] for x in _results if len(x) > j and not isinstance(x[j], str)]
                    if len(_list) != 0:
                        if (summary_type == 'best_and_average' and _fields[j] in average_list) \
                                or summary_type == 'average':
                            _res = sum(_list) / len(_list)
                        else:
                            _res = max(_list)
                    else:
                        _res = [x[j] for x in _results if len(x) > j if x[j] != '' or x[j] != None]
                        _res = _res[0] if len(_res) > 0 else ''
                    self.__add_best(_res if summary_type != 'none' else '')

                    # save best results in google sheet format if available
                    if len(self.gsheet_results) > j + 1:
                        self.gsheet_results[j + 1] = (_fields[j], _res)
                    else:
                        self.gsheet_results.append((_fields[j], _res))
            else:
                # save results in google sheet format
                for j in range(len(_fields)):
                    if len(self.gsheet_results) > j + 1:
                        self.gsheet_results[j + 1] = (_fields[j], _results[0][j])
                    else:
                        self.gsheet_results.append((_fields[j], _results[0][j]))
        finally:
            self.save()
