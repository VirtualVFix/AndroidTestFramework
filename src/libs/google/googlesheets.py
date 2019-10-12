# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Jun 29, 2016 3:31:29 PM$"

import os
import sys
import getpass
import httplib2
import datetime
import argparse
from time import time
from oauth2client import tools
from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage
from libs.path import find_path_by_regexp
from libs.core.logger import getLogger, getSysLogger
from libs.google.base.exceptions import SpreadsheetError
from .base.constants import KEY_DIR, SCOPES, APPLICATION_NAME, SERVICE_TIMEOUT


class GoogleSheets:
    """
    Class for manipulation with Google spreadsheet via Google API
    """
    def __init__(self, spreadsheet_id, sheet_identifier=0, client_file_name='atframeworkkey.json', logger=None):
        self.__client_file_name = client_file_name
        self.spreadsheet_id = spreadsheet_id
        self.logger = logger or getLogger(__file__)
        self.syslogger = getSysLogger()
        self.__service = None # autorized service
        self.__time = 0
        # get sheets info
        self.__getSheetsInfo(sheet_identifier)

    def get_credentials(self):
        """
        Gets valid user credentials from storage.
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            The obtained credential
        """
        credential_dir = os.path.join(KEY_DIR, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_name = getpass.getuser()+'.gsheets.googleapi.json'
        credential_path = find_path_by_regexp(KEY_DIR, credential_name, allow_environment_path=True)[0]
        if credential_path is None:
            credential_path = os.path.join(credential_dir, credential_name)
#        store = oauth2client.file.Storage(credential_path)
        store = Storage(credential_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(os.path.join(KEY_DIR,self.__client_file_name), SCOPES)
            flow.user_agent = APPLICATION_NAME
            keep_argv = sys.argv
            sys.argv = sys.argv[:1]
            flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
            self.logger.newline()
            self.logger.warning('Credentials authorization key for [%s] user is not found !' % getpass.getuser())
            self.logger.warning('Google API required access to your account ! '
                                + 'Please select your Motorola account in browser and confirm access !')
            self.logger.info('Waiting for account access confirmation...', self.syslogger)
            credentials = tools.run_flow(flow, store, flags)
            sys.argv = keep_argv
            # flush logger after waiting
            for x in self.logger.handlers:
                x.flush()
            self.logger.done(self.syslogger)
            self.syslogger.info('Storing credentials to ' + credential_path)
        return credentials

    @property
    def service(self):
        """
        Get authorized service
        """
        if self.__service is None or time()-self.__time > SERVICE_TIMEOUT:
            self.logger.info('Google API Credentials authorization...', self.syslogger)
            credentials = self.get_credentials()
            http = credentials.authorize(httplib2.Http())
            discovery_url = ('https://sheets.googleapis.com/$discovery/rest?version=v4')
            self.__service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discovery_url)
            self.__time = time()
        return self.__service

    def __getSheetsInfo(self, sheet_identifier=0):
        """
        Get all sheets and find all identification info for selected sheet

        Args:
            sheet_identifier (int or str, default 0): Identifier of sheet. It can be index, sheet id or sheet name.
                Type of identifier detected automatically

        Note:
            Function update the following variables:
                - self._sheet_name  # sheet name
                - self._sheet_id    # sheet id
                - self._sheet_index # sheet index in spreadsheet
        """

        try: sheet_identifier = int(sheet_identifier)
        except: pass
        # get info avout all sheets
        self.syslogger.info('Getting sheets info...')
        results = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id,
                                                  includeGridData=False).execute()
        if 'sheets' not in results:
            raise SpreadsheetError('Sheets info cannot be got !')
        # find not hidden sheets
        sheets = []
        for i in range(len(results['sheets'])):
            if not 'hidden' in results['sheets'][i]['properties'] or not results['sheets'][i]['properties']['hidden']:
                sheets.append((results['sheets'][i]['properties']['index'],
                               results['sheets'][i]['properties']['sheetId'],
                               results['sheets'][i]['properties']['title']))
        self.syslogger.info('Available and not hidden sheets: {}'.format(sheets))

        # get type of sheet identifier. Sheet identifier can be index of sheet, sheet id or sheet name
        sheets = tuple(zip(*sheets))
        type_of_identifier = -1
        if isinstance(sheet_identifier, int):
            if sheet_identifier < 1000:
                type_of_identifier = 0 # sheet index
            else:
                type_of_identifier = 1 # sheet id
        elif isinstance(sheet_identifier, str):
            type_of_identifier = 2 # sheet name
        else:
            raise SpreadsheetError('Sheet identifier should be integer or string ! '
                                   + 'Sheet identifier can be index of sheet, sheet id or sheet name.')

        # looking for identifier in sheets list
        index = -1
        for i in range(len(sheets[0])):
            if type_of_identifier == 2:
                if sheet_identifier.lower() == sheets[type_of_identifier][i].lower():
                    index = i
                    break
            elif sheet_identifier == sheets[type_of_identifier][i]:
                index = i
                break
        if index == -1:
            raise SpreadsheetError('Sheet with [%s] identifier not found ! ' % sheet_identifier
                                   + 'Sheet identifier can be index of sheet, sheet id or sheet name.')

        # save all sheet identifier
        self._sheet_index = sheets[0][index]  # sheet index in spreadsheet
        self._sheet_id = sheets[1][index]     # sheet id
        self._sheet_name = sheets[2][index]   # sheet name
        self._spreadsheet_title = results['properties']['title'] # spreadsheet title
        self.logger.info('Spreadsheet ID: "{}"'.format(self.spreadsheet_id))
        self.logger.info('Spreadsheet title: "{}"'.format(self._spreadsheet_title))
        self.logger.info('Selected sheet Name: "{}", Index: "{}", ID: "{}"'.format(self._sheet_name, self._sheet_index,
                                                                                   self._sheet_id))
        self.logger.info('Page: https://docs.google.com/spreadsheets/d/{}/edit#gid={}'.format(self.spreadsheet_id,
                                                                                              self._sheet_id))
        self.syslogger.info('Spreadsheet title: "{}". Selected sheet: Index: "{}", ID: "{}", Name: "{}"'
                            .format(self._spreadsheet_title, sheets[0][index], sheets[1][index], sheets[2][index]))

    def convertNameToIndex(self, name):
        """
        Convert column name like "AA" to index. Returns **name** if it's integer

        Args:
            name (str or int): Column name

        Returns:
            int: index
        """
        if isinstance(name, str):
            exp = 0
            index = 0
            for char in reversed(name):
                index += (ord(char.upper())-ord('A'))*(26**exp)
                exp += 1
            return index
        elif isinstance(name, int):
            return name
        else:
            raise SpreadsheetError('Type "{}" of Range "{}" is not supported !'.format(type(name), name))

    def convertIndexToName(self, index):
        """
        Convert index to column name like "AA". Returns **index** if it's string

        Args:
            index (str or int): Index to convert into name

        """
        if isinstance(index, int):
            letters = ''
            while True:
                letters += chr(index%26+ord('A'))
                index = index//26
                if index == 0:
                    break
            return ''.join(reversed(letters))
        elif isinstance(index, str):
            return index.upper()
        else:
            raise SpreadsheetError('Type "{}" of Index "{}" is not supported !'.format(type(index), index))

    def insertColumn(self, insert_before_index=3, columns_count=1, inheritFromBefore=False):
        """
        Insert column to spreadsheet in "sheet_id" tab.

        Args:
            insert_after_index (int, default 3): Column index before which need to insert. (zero-based index).
            columns_count (int, default 1): Columns count for insert
            inheritFromBefore (bool, default False): Copy background from left column if true or from right
                column if false
        """
        requests = []
        requests.append({"insertDimension":{
                            "range": {
                                "sheetId": self._sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": insert_before_index,
                                "endIndex": insert_before_index+columns_count
                            },
                            "inheritFromBefore": str(inheritFromBefore).lower()
                        }})
        batchUpdateRequest = {'requests': requests}
        results = self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id,
                                                          body=batchUpdateRequest).execute()
        return results

    def getDataFromColumn(self, data_range='A:A', valueRenderOption='FORMATTED_VALUE'):
        """
        Get values without metadata by range.
        Range should be specified in spreadsheet style like "A10:A20" without sheet name

        Args:
            data_range (str, default 'A:A'): Data range in spreadsheet style like "A10:A20"
            valueRenderOption (str, default 'FORMATTED_VALUE'): Value render option

        Note:
            Allowed the following value render options:
                - FORMATTED_VALUE: Values will be calculated & formatted in the reply according to the cell's
                  formatting. Formatting is based on the spreadsheet's locale, not the requesting user's locale.
                  For example, if A1 is 1.23 and A2 is =A1 and formatted as currency, then A2 would return "$1.23".
                - UNFORMATTED_VALUE: Values will be calculated, but not formatted in the reply. For example,
                  if A1 is 1.23 and A2 is =A1 and formatted as currency, then A2 would return the number 1.23.
                - FORMULA: Values will not be calculated. The reply will include the formulas. For example,
                  if A1 is 1.23 and A2 is =A1 and formatted as currency, then A2 would return "=A1".
        """
        results = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id,
                                                           range="{}!{}".format(self._sheet_name, data_range),
                                                           valueRenderOption=valueRenderOption).execute()
        return [x for x in results['values']]

    def getDataOfColumnWithMetaData(self, data_range='A:A'):
        """
        Get values with metadata by range in spreadsheet style like "A10:A20"

        Args:
            data_range (str): Data range. Should be specified without sheet name
        """
        results = self.service.spreadsheets().get(spreadsheetId=self.spreadsheet_id,
                                                  includeGridData=True,
                                                  ranges="{}!{}".format(self._sheet_name, data_range)).execute()
        return results['sheets'][0]['data'][0]

    def convertValuesToRequest(self, row_index, column_index, values, formats=None):
        """
        Update values in sheet.

        Args:
            row_index (int): Row index for insert (zero-based index).
            column_index (int): Column index for insert (zero-based index).
            values (list of dict, list of list or list of tuple): Values list. Values can be dictionary with format
            formats (dict): Formats of data. Background, color and etc.

        Example:
            .. code-block:: python

                # Values in different type
                values = [] or [{},{}] or [[],[]] or [(),()]
                # Values with format
                values = [{'value':1,
                           'format': {'backgroundColor': {'green':1}},
                           {}]
                # Data format
                format = {'backgroundColor': {'green':1}}

        Returns:
            dict: Request body
        """
        # add used formats to request
        format_list = []

        def addFormats(key_list):
            for x in key_list:
                if not x in format_list:
                    format_list.append(x)

        # add value to reqiest
        def toUserEnteredValue(value):
            if isinstance(value, (int, float)):
                return {'userEnteredValue': {'numberValue': value}}
            elif isinstance(value, str):
                return {'userEnteredValue': {'stringValue': value}}
            elif isinstance(value, datetime.datetime):
                return {'userEnteredValue': {'numberValue': (value-datetime.datetime(1899, 12, 31, 0, 0)).days+1}}
            elif value is None:
                return {'userEnteredValue': {'stringValue': ''}}
            else: raise SpreadsheetError('Type of Value "{}" is not supported for sheet update !'.format(value))

        # add value and format to request
        def toRequestValueWithFormat(value):
            if isinstance(value, dict):
                _value = value['value']
                tmp = toUserEnteredValue(_value)
                tmp['userEnteredFormat'] = value['format']
                addFormats(value['format'].keys())
                return tmp
            else:
                _value = value
                tmp = toUserEnteredValue(_value)
                if formats is not None:
                    addFormats(formats.keys())
                    tmp['userEnteredFormat'] = format
                return tmp

        # row request
        rows_request = []
        for val in values:
            if isinstance(val, (list, tuple)):
                tmp = []
                for x in val:
                    tmp.append(toRequestValueWithFormat(x))
                rows_request.append({'values':tmp})
            else:
                rows_request.append({'values':[toRequestValueWithFormat(val)]})
        # add values request
        requests = [{'updateCells': {'start': {'sheetId': self._sheet_id, 'rowIndex': row_index,
                                               'columnIndex': column_index},
                                     'rows': rows_request,
                                     'fields': 'userEnteredValue' + (lambda l: ',userEnteredFormat.'
                                                                               + ',userEnteredFormat.'
                                                                     .join(l) if len(l)>0 else '')(format_list)
                                     }
                     }]
        return requests

    def getValues(self, data_range):
        """
        Get benchmark values by range

        Args:
             data_range (str, default 'A:A'): Data range in spreadsheet style like "A10:A20"

        Returns:
            list: Values
        """
        row_data = self.getDataOfColumnWithMetaData(data_range)
        results = []
        for i in range(len(row_data['rowData'])):
            data = row_data['rowData'][i]['values'][0]
            value = data['effectiveValue']['stringValue'] if 'effectiveValue' in data \
                                                             and 'stringValue' in data['effectiveValue'] \
                else data['effectiveValue']['numberValue'] if 'effectiveValue' in data \
                                                              and 'numberValue' in data['effectiveValue'] \
                else data['formattedValue'] if 'formattedValue' in data else None
            results.append(value)
        return results

    def updateValues(self, requests):
        """
        Upload values to spreadsheet
        Args:
            requests (dit): Update request converted with :func:`convertValuesToRequest` function

        Returns:
            response body
        """
        batchUpdateRequest = {'requests': requests}
        results = self.service.spreadsheets().batchUpdate(spreadsheetId=self.spreadsheet_id,
                                                          body=batchUpdateRequest).execute()
        return results
