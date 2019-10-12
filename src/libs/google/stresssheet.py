# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Jul 4, 2016 2:50:28 PM$"

import re
from .googlesheets import GoogleSheets
from libs.core.logger import getLoggers
from .base.constants import UPDATE_REQUEST_LIMIT
from libs.google.base.exceptions import SpreadsheetError, SpreadsheetResultError


class StressSheet(GoogleSheets):
    def __init__(self, spreadsheet_id, sheet_identifier=0, client_file_name='atframeworkkey.json', logger=None):
        super(StressSheet, self).__init__(spreadsheet_id, sheet_identifier, client_file_name,
                                          logger=logger or getLoggers(__file__))
        
    def getTestNamesData(self, row_data, names_index=1):
        """
        Get test data included: test names

        Args:
            row_data (dict): Row date from sheet
            names_index (int): Index of column with benchmark names (zero-based index)

        Returns:
             list: List of

        Return list format:
            .. code-block:: python

                return [(row_index,   # row index of test name
                         test_name),   # test name. Text on white background
                        ...]
        """
        values_len = len(row_data['rowData'][0]['values'])-1
        if names_index > values_len: 
            raise SpreadsheetError('Index "{}" of column with names not in sheet !'.format(names_index))
        results = []

        for i in range(len(row_data['rowData'])):
            data = row_data['rowData'][i]['values'] if 'values' in row_data['rowData'][i] else None
            if data is not None:
                meta = row_data['rowMetadata'][i]
                color = data[names_index]['effectiveFormat']['backgroundColor'] \
                    if names_index < len(data) and 'effectiveFormat' in data[names_index] else None
                name = data[names_index]['formattedValue'] if names_index < len(data) and 'formattedValue' \
                                                              in data[names_index] else ''
                hidden = meta['hiddenByUser'] if 'hiddenByUser' in meta else False
                # if text on white background
                if not hidden and name.strip() != '' and 'deprecated' not in name.lower():
                    if not color is None and color.values() == [1,1,1]:
                        results.append((i, name))
        return results
    
    def updateHeaderMap(self, row_data, end_index, header_map):
        """
        Find header by regexp or index and return updated header map

        Args:
            row_data (dict): Row data of column. Start from 0
            end_index (int): End index of header data (search until end_index row only)
            header_map (list): Headers configuration map list

        Header map format:
            .. code-block:: python

                header_map=[{'regex':string,       # search regexp if row not set
                             'row':int,            # row index (should exists row or regex field)
                             'def_value':string}]  # value by default if available

        Returns:
            list: List of find headers from header_map

        Return list format:
            .. code-block:: python

                [{'row':int,           # row index of header. Start from 0.
                  'regex':string,      # search regexp if row not set
                  'name':string,       # name for reports
                  'def_value':string}] # value by default if available
        """
        # find headers in sheet
        results = []
        used_index_list = []
        for header in header_map: 
            assert 'row' in header or 'regex' in header, 'Header map should contain "row" or "regex" field !'
            tmp = None
            for i in range(end_index): # search until end_index row only
                if i in used_index_list: 
                    continue
                data = row_data['rowData'][i]['values'][0] if 'values' in row_data['rowData'][i] else None
                
                if data is not None:
                    name = data['formattedValue'] if 'formattedValue' in data else ''
                    if ('row' in header.keys() and header['row'] == i) or \
                       ('regex' in header.keys() and re.search(header['regex'], name, re.I)):
                        tmp = {'row': i, 
                               'name':name, 
                               'def_value': header['def_value'] if 'def_value' in header.keys() else None}
                        break
            if tmp is None: 
                raise SpreadsheetError('Header "{}" is not found !'.format(header['row'] if 'row' in header.keys()
                                                                           else header['regex']))
            results.append(tmp)
            used_index_list.append(tmp['row'])  #(i)
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
        data_range = [x[0]+1 for x in header_list]
        if not rewrite: 
            if current_header is None:
                current_values = self.getValues('{0}1:{0}{1}'.format(values_column_name, max(data_range)))
            else:
                current_values = current_header
        else:
            current_values = [None for x in range(max(data_range))]
        
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
            requests.append(self.convertValuesToRequest(start_row, self.convertNameToIndex(values_column_name), values))
        
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
        warnings = []  # warning list
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
