# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "13/10/17 20:54"

from config import CONFIG
from libs.core.unittest import Wait
from libs.core.unittest import Tools
from libs.core.options import Options
from libs.core.logger import getLoggers
from optparse import OptionGroup, SUPPRESS_HELP
from libs.core.exceptions import RuntimeInterruptError


class Info(Options):
    """
    Test information options.
    """

    def __init__(self):
        super(Info, self).__init__()
        self.logger, self.syslogger = getLoggers(__file__)
        # Used to print empty documentation line in TestCase ot TestSuites description
        self.empty_doc_line = '-'
        # Used to print empty variable description
        self.no_description = 'No description'

    def group(self, parser):
        group = OptionGroup(parser, 'Test information')
        group.add_option('--case-list', dest='case_list', action="store_true", default=False,
                         help='Print all available TestCases.')
        group.add_option('--suite-list', dest='suite_list', action="store_true", default=False,
                         help='Print all available TestSuites for TestCases defined in [--tests] option.')
        group.add_option('--test-list', dest='test_list', action="store_true", default=False,
                         help='Print all available Test for selected TestSuites of selected TestCases defined '
                              + 'in [--tests] option.')
        group.add_option('--variable-list', dest='variable_list', action="store_true", default=False,
                         help='Print all available Variables of Tests for selected TestSuites of '
                              + 'selected TestCases defined in [--tests] option.')
        group.add_option('--var-list', dest='variable_list', action="store_true", default=False, help=SUPPRESS_HELP)
        group.add_option('--preset-list', dest='preset_list', action="store_true", default=False,
                         help='Print all available Presets.')
        return group

    @property
    def priority(self):
        return 980

    def table_header(self, suite_decor=True):
        """ Print TestCases with TestSuite table header part """
        self.logger.table('=*')
        self.logger.table(('TestCase'.upper(), 35, 'center'),
                          ('TestSuite'.upper(), 20, 'center'),
                          ('TestSuite Description'.upper(), 'center'))
        self.logger.table('-*')
        printed = []
        for i, case in enumerate(sorted(CONFIG.UNITTEST.SELECTED_TEST_CASES, key=lambda x: x['name'])):
            # ignore duplicate cases
            if case['name'] not in printed:
                for j, (suite) in enumerate(sorted(case['suites'], key=lambda x: x['name'])):
                    if j > 0 and (suite_decor is True or suite_decor is False):
                        self.logger.table('-*')
                    self.logger.table((case['name'], 35, 'center'),
                                      (suite['name'], 20, 'center'),
                                      (suite['doc'] or self.empty_doc_line, 'center'))
                    if suite_decor is True:
                        self.logger.table('-*')
                    yield (i, case, j, suite)
                printed.append(case['name'])
        self.logger.table('=*')

    async def validate(self, options):
        if len([0 for x in [options.case_list, options.suite_list,
                            options.test_list, options.variable_list] if x is True]) > 1:
            raise RuntimeInterruptError('[--case-list], [--suite-list], [--test-list], [--variable-list] '
                                        + 'and [--preset-list] options are mutually exclusive !')

        # --case-list option
        if options.case_list is True:
            # wait for available TestCases
            await Wait.wait_for_available_cases()

            self.logger.table('=*')
            self.logger.table(('TestCase'.upper(), 35, 'center'), ('Description'.upper(), 'center'))
            self.logger.table('-*')

            for case in sorted(CONFIG.UNITTEST.AVAILABLE_TEST_CASES):
                self.logger.table((case, 35, 'center'),
                                  (CONFIG.UNITTEST.AVAILABLE_TEST_CASES[case]['doc'] or self.empty_doc_line, 'center'))
            self.logger.table('=*')
            # interrupt Framework launch
            raise RuntimeInterruptError

        # --suite-list option
        elif options.suite_list is True:
            # wait for selected TestCases
            await Wait.wait_for_selected_cases()

            for i, case, j, suite in self.table_header(suite_decor=False):
                # do nothing
                pass

            # interrupt Framework launch
            raise RuntimeInterruptError

        # --test-list option
        elif options.test_list is True:
            # wait tests
            await Wait.wait_for_load_tests()

            for i, case, k, suite in self.table_header(suite_decor=False):
                self.logger.table('-*')
                self.logger.table(('#'.upper(), 5, 'c'), ('Test Name'.upper(), 16, 'c'),
                                  ('Second Test Name'.upper(), 20, 'c'), ('Test Description'.upper(), 'c'))
                self.logger.table('- *')

                # print tests
                shown = []
                for j, test in enumerate(suite['tests']):
                    if test['id'] not in shown:
                        self.logger.table((j+1, 5, 'c'),
                                          (test['id'], 16, 'c'),
                                          (test['name'] or self.empty_doc_line, 20, 'c'),
                                          (test['desc'] or self.empty_doc_line, 'c'))
                    shown.append(test['id'])
                if k < len(case['suites'])-1:
                    self.logger.table('-*')

            # interrupt Framework launch
            raise RuntimeInterruptError

        # --variable-list option
        elif options.variable_list is True:
            # wait for selected TestCases
            await Wait.wait_for_selected_cases()

            for i, case, k, suite in self.table_header(suite_decor=True):
                # parse variables
                try:
                    var, real = Tools.get_class_variables(suite['class'], suite['path'])
                except Exception as e:
                    raise RuntimeInterruptError(e)

                self.logger.table(('Variable = default value'.upper(), 35, 'c'), ('description'.upper(), 'c'))
                self.logger.table('- *')

                if len(var) == 0 and len(real) == 0:
                    self.logger.table(('No variables are found !'.upper(), 'center'))
                    continue

                shown = []
                # print parsed variables
                for j, (name, val, desc) in enumerate(var):
                    if name in real:
                        self.logger.table(('%s = %s' % (name, val), 35),
                                          desc.capitalize() or self.no_description)
                        if j < len(var)-1:
                            self.logger.table(' *')
                    shown.append(name)

                # print missing variables
                for j, name in enumerate(sorted(real)):
                    if name not in shown:
                        self.logger.table(('%s = %s' % (name, getattr(suite['class'], name)), 35),
                                          self.no_description)
                        if j < len(var) - 1:
                            self.logger.table(' *')

            # interrupt Framework launch
            raise RuntimeInterruptError

        # --preset-list
        elif options.preset_list is True:
            self.logger.WARNING('PRESET LIST NOT IMPLEMENTED YET !')
            # interrupt Framework launch
            raise RuntimeInterruptError
