# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Jul 6, 2016 12:50:47 PM$"

from config import CONFIG
from libs.core.logger import getLogger
from libs.google import BenchmarkSheet
from libs.google.base.exceptions import SpreadsheetError


class AutoBenchmarks(BenchmarkSheet):
    def __init__(self, spreadsheet_id, sheet_identifier=0, client_file_name='atframeworkkey.json', logger=None):
        if spreadsheet_id is None or len(spreadsheet_id) < 10: 
            raise SpreadsheetError('Spreadsheet ID is not defined ! Please define device name or platform in '
                                   + '"device" variable or spreadsheet ID in "spreadsheet_id" variable !')
        super(AutoBenchmarks, self).__init__(spreadsheet_id, sheet_identifier, client_file_name,
                                             logger=logger or getLogger(__file__))
        self.logger.newline()
        self.logger.info('FULL AUTOMATE MODE IS ENABLED !')
        self.logger.newline()
        # google sheet settings -------------------------------------------------
        self.sheet_names_column = 'A'     # Identifier of column with test names. Can be columnd name or index.
        self.sheet_trends_column = 'C'    # Identifier of column with trend formula. Can be columnd name or index.
        self.sheet_results_column = 'D'   # Identifier of column with values or previous results fot compare. Can be columnd name or index.
        self.sheet_new_column = True      # Save results to new column. Results will be saved to "sheet_values_column" column if == False.
        self.sheet_header_rewrite = False # Insert results to sheet_values_column column without insert new one.  
        self.header_config = []           # Sheet header configuration
        # format for regular results
        self.format_regular = {'backgroundColor': {'green':1,'blue':1,'red':1}, 
                               'horizontalAlignment': 'CENTER',
                               'verticalAlignment': 'MIDDLE'}
        # format for failed resutls
        self.format_failed = {'backgroundColor':  {'blue': 0.41960785, 'green': 0.49411765, 'red': 0.86666667}, 
                              'horizontalAlignment': 'CENTER',
                              'verticalAlignment': 'MIDDLE',
                              'wrapStrategy': 'WRAP'}
        # ----------------------------------------------------------------------
        # wrong spreadsheet warning
        if not CONFIG.DEVICE.DEVICE_NAME.lower() in self._spreadsheet_title.lower() \
                and not CONFIG.DEVICE.CPU_HW.lower() in self._spreadsheet_title.lower():
            self.logger.newline()
            self.logger.warn('DEVICE NAME ("%s") OR PLATFORM ("%s") ARE NOT FOUND IN SPREADSHEET TITLE ("%s") ! '
                             % (CONFIG.DEVICE.DEVICE_NAME, CONFIG.DEVICE.CPU_HW, self._spreadsheet_title)
                             + 'PLEASE MAKE SURE, THAT YOU USE CORRECT SPREADSHEET !')
            self.logger.newline()
        
    def prepareSheet(self):
        """ Prepare sheet """
        self.logger.info('Preparing spreadsheet...')
        self.logger.info('Searching tests names...')
        # get row data
        names_row_data = self.getDataOfColumnWithMetaData('%s:%s' % (self.convertIndexToName(self.sheet_names_column),
                                                                     self.convertIndexToName(self.sheet_trends_column)))
        # get benchmarks data
        self.testNamesData = self.getTestNamesData(names_row_data, 
                                                   names_index=self.convertNameToIndex(self.sheet_names_column),
                                                   trends_index=self.convertNameToIndex(self.sheet_trends_column))
        # insert new column
        if self.sheet_new_column:
            self.logger.info('Inserting new column to "{}" sheet.'.format(self._sheet_name))
            self.insertColumn(insert_before_index=self.convertNameToIndex(self.sheet_results_column), columns_count=1,
                              inheritFromBefore=False)
        else: 
            self.logger.newline()
            self.logger.warn('NEW COLUMN WILL NOT CREATED. PLEASE NOTE, VALUES {}IN "{}" COLUMN COULD BE REWRITTEN !'
                             .format('(EXCEPT HEADER) ' if not self.sheet_header_rewrite else '',
                                     self.sheet_results_column))
            self.logger.newline()
            
        # update header config
        self.logger.info('Updating header...')
        if len(self.header_config) == 0:
            raise SpreadsheetError('Sheet header is not defined !')
        # update header 
        self.header_config = self.getHeaders(names_row_data, self.testNamesData[0][0], header_config=self.header_config)
        self.updateHeaderConfig()
          
    def updateHeaderConfig(self):
        """ return updated header config """
        self.updateHeader(self.header_config, self.convertIndexToName(self.sheet_results_column),
                          rewrite=self.sheet_header_rewrite)

    def updateResults(self, results):
        """ Upload results to google spreadsheet """
        self.logger.info('Uploading "{}" results to "{}" spreadsheet -> "{}" sheet...'.format(results[0],
                                                                                              self._spreadsheet_title,
                                                                                              self._sheet_name))
        self.logger.info('Page: https://docs.google.com/spreadsheets/d/{}/edit#gid={}'.format(self.spreadsheet_id,
                                                                                              self._sheet_id))
        self.updateBenchmartkResults(self.testNamesData, self.sheet_results_column, results, self.format_regular,
                                     self.format_failed)
        self.logger.info('Done')
    
    def createCR(self):
        pass
    
    def closeCR(self):
        pass
    
    def sendReport(self):
        pass
