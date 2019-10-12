# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Jul 4, 2016 2:50:28 PM$"

import re
from libs.core.logger import getLoggers
from .googlesheets import GoogleSheets
from .base.constants import UPDATE_REQUEST_LIMIT
from libs.google.base.exceptions import SpreadsheetError, SpreadsheetResultError


class BenchmarkSheet(GoogleSheets):
    def __init__(self, spreadsheet_id, sheet_identifier=0, client_file_name='atframeworkkey.json', logger=None):
        super(BenchmarkSheet, self).__init__(spreadsheet_id, sheet_identifier, client_file_name,
                                             logger=logger or getLoggers(__file__))
        
    def _getTrendFromFormula(self, formula, up_trend_symbol='\xe2\x86\x91', down_trend_symbol='\xe2\x86\x93'):
        """
        Dump trend formula from sheet

        Args:
            formula (str or byte): Trend formula
            up_trend_symbol (str): Up arrow symbol in trend formula
            down_trend_symbol (str): Down arrow symbol in trend formula

        Returns:
            int: 1 if trend up (more result value is better), -1 otherwise or 0 if trend is N/A
        """
        try:
            formula = formula.decode('utf-8')
        except:
            pass

        if formula == '':
            return 0

        up_index = formula.find(up_trend_symbol)
        down_index = formula.find(down_trend_symbol)
        
        if up_index < 0 or down_index < 0:
            return 0
        return 1 if up_index < down_index else -1
        
    def getTestNamesData(self, row_data, names_index=0, trends_index=2):
        """
        Get benchmarks data included: benchmark names, trend formulas and previous run values is available
        Benchmarks marked as "deprecated" in name or benchmarks with hidden fields will be skipped.

        Args:
            row_data (dict): Row date from sheet
            names_index (int, default 0): Index of column with benchmark names (zero-based index).
            trends_index (int, default 2): Index of column with trend formulas (zero-based index).

        Returns:
            list: List of test names and trends data

        Return list format:
            .. code-block:: python

                [[start_row,         # row index of benchmark name 
                  benchmark name,    # benchmark name. Text should be bold style with non white background
                  (benchmark filed1, # benchmark filed. Regular text 
                   trend,            # result of trend detected by formula in trends_index column. 1 if trend up (more result value is better), -1 otherwise or 0 if trend is N/A,
                   format),          # save user entered format
                  (benchmark filed2, trend),
                 ...],
                ...]
        """
        values_len = len(row_data['rowData'][0]['values'])-1
        if names_index > values_len: 
            raise SpreadsheetError('Index "{}" of column with names not in sheet !'.format(names_index))
        if trends_index > values_len: 
            raise SpreadsheetError('Index "{}" of column with trend not in sheet !'.format(trends_index))

        results = []
        tmp = []
        # group values by format
        for i in range(len(row_data['rowData'])):
            data = row_data['rowData'][i]['values'] if 'values' in row_data['rowData'][i] else None
            if data is not None:
                meta = row_data['rowMetadata'][i]
                bold = data[names_index]['effectiveFormat']['textFormat']['bold'] \
                    if names_index < len(data) and 'effectiveFormat' in data[names_index] else False
                color = data[names_index]['effectiveFormat']['backgroundColor'] \
                    if names_index < len(data) and 'effectiveFormat' in data[names_index] else None
                name = data[names_index]['formattedValue'] if names_index < len(data) \
                                                              and 'formattedValue' in data[names_index] else ''
                trend = self._getTrendFromFormula(data[trends_index]['userEnteredValue']['formulaValue']
                                                  .encode('utf-8') if trends_index < len(data)
                                                                      and 'userEnteredValue' in data[trends_index]
                                                                      and 'formulaValue'
                                                                      in data[trends_index]['userEnteredValue'] else '')
                hidden = meta['hiddenByUser'] if 'hiddenByUser' in meta else False
                format = data[names_index]['userEnteredFormat'] if 'userEnteredFormat' in data[names_index] else None
                if hidden: tmp = [] # skip all values if find hidden text
                # if text is bold and background is not white
                if name.strip() != '':
                    if bold and not color is None and color.values() != [1,1,1]:
                        if len(tmp) > 2:
                            results.append(tmp) # put values if benchmark have result fileds
                        if 'deprecated' in name.lower():
                            tmp = [] # skip depricated tests
                        else: tmp = [i, name] # add i as offset of range to benchmark name
                    elif len(tmp) != 0: # start only when benchmark header is found
                        tmp.append((name, trend, format))
        if len(tmp) > 2:
            results.append(tmp)
        return results
    
    def getHeaders(self, row_data, end_index, header_config):
        """
        Find header by regexp or index

        Args:
            row_data (dict): Row data of column
            end_index (int): End index of header data
            header_config (list): Headers configuration

        Header configuration format:
            .. code-block:: python

                header_config=[('regex',        # regexp or int index of row
                                'report name',  # name for reports
                                'default value' # value by default if available
                               ), ...]

        Returns:
            list: List of find headers from header_config in the same order

        Return list:
            .. code-block:: python

                [[start_row,       # row index of benchmark name
                  header_name,     # benchmark name. Text should be bold style with non white background
                  report_name,     # name for reports
                  default_value],  # default value of header
                ...]
        """
        # find headers in sheet
        results = []
        used_index_list = []
        for header in header_config: 
            tmp = None
            for i in range(end_index): # search in first 20 columns only
                if i in used_index_list: continue
                data = row_data['rowData'][i]['values'][0]
                name = data['formattedValue'] if 'formattedValue' in data else ''
                if isinstance(header[0], int) and header[0] == i:
                    tmp = [i, name, header[1], header[2] if len(header) > 2 else None]
                    break
                match = re.search(header[0], name, re.I)
                if match: 
                    tmp = [i, name, header[1], header[2] if len(header) > 2 else None]
                    break
            if tmp is None: raise SpreadsheetError('Header "{}" is not found by "{}" identifier !'
                                                   .format(header[0], header[1]))
            results.append(tmp)
            used_index_list.append(tmp[0])
        return results

    def updateHeader(self, header_list, values_column_name, current_header=None, rewrite=False):
        """
        Update header

        Args:
            header_list (list): Header list to write
            values_column_name (str): Name or index of column with values in sheet
            current_header (list, default None): Current header list to update values only
            rewrite (bool, default False): Allow to rewrite values
        """
        # update requests
        requests = []
        
        # get current values
        _range = [x[0]+1 for x in header_list]
        if not rewrite: 
            if current_header is None:
                current_values = self.getValues('{0}1:{0}{1}'.format(values_column_name, max(_range)))
            else:
                current_values = current_header
        else:
            current_values = [None for x in range(max(_range))]
        
        # get header update requests only for values need to update
        values = []
        start_row = 0
        added_row = 0
        for header in header_list:
            row = header[0]
            if row-1 != added_row and len(values) > 0:
                requests.append(self.convertValuesToRequest(start_row, self.convertNameToIndex(values_column_name),
                                                            values))
                values = []
            if (current_values[row] is None or (isinstance(current_values[row], str)
                                                and current_values[row].strip() == '')) \
                and not header[3] is None and str(header[3]).strip() != '':
                if len(values) == 0: start_row = row
                values.append(header[3])
                added_row = row
        if len(values) > 0:
            requests.append(self.convertValuesToRequest(start_row, self.convertNameToIndex(values_column_name),
                                                        values))
        
        # update values
        if len(requests) > 0: 
            self.updateValues(requests)
        
    def updateBenchmartkResults(self, names_data, results_column, values, regular_format, failed_format):
        """
        Update values

        Args:
            names_data (list): List of names
            results_column (str): Result column name of index
            values (list): Values list
            regular_format (dict): Regular data format
            failed_format (dict): Error data format
        """
        warnings = [] # warning list
        name = values[0]
        name_fields = None
        
        for x in names_data:
            if name.lower() in x[1].lower():
                name_fields = x
        if name_fields is None: 
            warnings.append(name)
            raise SpreadsheetResultError('Benchmark "{}" not found in "{}" sheet !'.format(name, self._sheet_name))
        
        results = []
        latest_index = 1
        for i in range(2, len(name_fields), 1):
            current_format = name_fields[i][2]
            name_field = re.sub('\[.*\]','',name_fields[i][0]).strip().lower()
            name_value = re.sub('\[.*\]','',values[latest_index][0]).strip().lower()
            if name_field == name_value:
                results.append({'value': values[latest_index][1],
                                'format': current_format if (values[latest_index][1] is None
                                                             and current_format is not None) else regular_format
                                if isinstance(values[latest_index][1],(int,float)) else failed_format})
                if latest_index+1 < len(values):
                    latest_index += 1
            else:
                self.logger.warn('Field "{}" not found in results !'.format(name_fields[i][0]))
                results.append({'value': '',
                                'format': failed_format})
                warnings.append(name_fields[i])                

        # update values
        if len(results) > 0:
            for i in range(0, len(results), UPDATE_REQUEST_LIMIT):  # values limit for one request
                requests = (self.convertValuesToRequest(name_fields[0]+i+1, self.convertNameToIndex(results_column),
                                                        results[i:i+UPDATE_REQUEST_LIMIT]))
                self.updateValues(requests)
        return warnings
