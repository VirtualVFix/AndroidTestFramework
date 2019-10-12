# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "13/10/17 20:54"

from config import CONFIG
from optparse import OptionGroup
from libs.core.options import Options
from libs.core.logger import getLoggers
from libs.core.unittest import filter, Tools
from libs.core.exceptions import RuntimeInterruptError


class Exec(Options):
    """
    Test execute options.
    """

    def __init__(self):
        super(Exec, self).__init__()
        self.logger, self.syslogger = getLoggers(__file__)

    def group(self, parser):
        group = OptionGroup(parser, 'Test execute filter')
        group.add_option('-t', '--tests', dest='tests',
                         default=CONFIG.SYSTEM.DEFAULT_TEST if hasattr(CONFIG.SYSTEM, 'DEFAULT_TEST') else None,
                         help='Filter TestCases to run. Use comma "," as delimiter to specify one more TestCases '
                              + 'Usage: -t "testCase1, testCase2". '
                              + 'TestCases may be duplicated to configure same TestSuites with different parameters. '
                              + 'Use [--case-list] option to print all available TestCases.')
        group.add_option('-i', '--include', dest='include', default=None,
                         help='Filter TestSuites to run from selected TestCase [--tests] option. '
                              + 'Usage: -i "[-]testSuite1,[-]testSuite2; [-]testSuite1". '
                              + 'Minus symbol [-] is optional and change filter behavior '
                              + 'to exclude TestSuite from run. '
                              + 'Use semicolon ";" as delimiter to combine set of TestSuites for each TestCase '
                              + 'specified in [--tests] option. '
                              + 'TestSuites sets should be in same order as defined in the [--tests] option. '
                              + 'TestSuites inside set should be delimited by comma ",". '
                              + 'Use [--suite-list] option to print all available TestSuites.')
        group.add_option('-p', '--parameters', dest='parameters', default=None,
                         help='Filter Tests to run from TestSuite or change variables values defined in '
                              + 'TestSuite class. Usage: -p "#TestSuiteName1: [-/*]testName or testShortDescription, '
                              + 'variable1=value1, variable2=value2, #TestSuiteName2: [-]testName; '
                              + 'Minus symbol [-] is optional and change filter behavior to exclude Test from run. '
                              + 'Asterisk symbol [*] is optional and affect Test order. All Tests with asterisk '
                              + 'will be started with first priority. Asterisk symbol cannot be combined with minus ! '
                              + 'Parameters for different TestCases should be separated by semicolon [;] and must be '
                              + 'specified in the same order as defined in the [--test] option. '
                              + 'All parameters are not case sensitive. '
                              + 'Use [--test-list] option to print all available Tests.')
        group.add_option('--preset', dest='preset', default=None,
                         help='Run Preset of tests. Usage: --preset "presetName, testCaseName.presetName" '
                              + 'Presets may be global (TestCases preset) and local (preset in TestCase). '
                              + 'Add name of all parent TestCases to specify local preset. '
                              + 'Example: --preset "benchmarks.3d" # Local preset [3d] in [benchmarks] TestCase)')
        return group

    @property
    def priority(self):
        return 990

    # def setup(self):
    #     # raise Exception('asd')
    #     print('setup test in lib')
    #     return 1+1

    async def validate(self, options):
        # Cases not specified
        cases = Tools.convert_str_cases_to_list(options.tests)
        if (len(cases)) == 0 and not (options.self_test is True
                                      or options.case_list is True
                                      or options.suite_list is True):
            raise RuntimeInterruptError("No one TestCase was specified in [--test] option ! "
                                        + "Use [--case-list] to print all available TestCases")
        # filter by --preset
        if options.preset is not None:
            await filter.Preset.filter_by_preset(options.preset)
        else:
            # filter by --tests option
            await filter.Case.filter_by_cases(options.tests)
            # filter by --include option
            await filter.Suite.filter_by_suite(options.include)
            # filter by --parameters option
            await filter.Params.filter_by_params(options.parameters)

        # lock changes after all filters
        # CONFIG.UNITTEST.LOCK('SELECTED_TEST_CASES')

        # print(CONFIG.UNITTEST.SELECTED_TEST_CASES)
        # print(' ')
        # print('+++', [[(case['name'], case['index'], suite['name'], id(suite['class']), suite['filters'],
        #                 [(test['id'], id(test['test'])) for test in case['suites'][i]['tests']])
        #                for i, suite in enumerate(case['suites'])]
        #               for case in CONFIG.UNITTEST.SELECTED_TEST_CASES], '+++')
        # print('+++', [[(suite['name'], [(test['id'], test['index']) for test in case['suites'][i]['tests']])
        #                for i, suite in enumerate(case['suites'])]
        #               for case in CONFIG.UNITTEST.SELECTED_TEST_CASES], '+++')

        # if self.options.preset:
        #     self.logger.info('Used preset: {}'.format(self.options.preset))
