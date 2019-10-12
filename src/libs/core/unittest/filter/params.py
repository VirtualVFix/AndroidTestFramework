# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "12/5/2017 5:36 PM"

import ast
import copy
import inspect
from ..wait import Wait
from ..tools import Tools
from config import CONFIG
from libs.core.template import NAME, SUITE_FULL
from libs.core.logger import getLoggers, getSysLogger
from ..exceptions import ParametersParseError, TestNotFoundError, VariableFoundError


class Params:
    """
    UnitTest filter class
    """
    @staticmethod
    def set_auto_variable(cls, name, value, suite):
        """
        Check if variable is auto variable. And also check variable correction.

        Note:
            Auto variables may not be present in class by may be specified in parameters.
            Current auto variables list:

                - Variables with name of Test function or second Test name and ends with ***_cycles**

        Args:
            cls (class): Class for setup variable
            name (str): Variable name
            value (any): Variable value
            suite (dict): Suite for error message and to add filter

        Returns:
            True if variable was set False otherwise
        """
        added = False
        if name.lower().endswith('_cycles'):
            cor_name = Tools.convert_name_to_variable(name).lower()
            test_name = cor_name[:cor_name.rfind('_')]

            # check tests
            for test in suite['tests']:
                second = Tools.convert_name_to_variable(test['name']) if test['name'] is not None else None
                if test['id'] == test_name or second == test_name:
                    if isinstance(value, (int, float)):
                        # add testXX_cycles variable
                        setattr(cls, '%s_cycles' % test['id'], int(value))
                        # add name_cycles variable if exists
                        if second is not None:
                            setattr(cls, '%s_cycles' % second, int(value))
                        added = True
                    else:
                        raise ParametersParseError(
                            'Inconsistent value type for "%s=%s" variable: expected - [%s] or [%s], found - [%s]'
                            % (name, value, type(int), type(float), type(value)))
        return added

    @staticmethod
    def get_variable_name(cls, name):
        """
        Case insensitive check if class has variable.

        Args:
            cls (class): Class to check variable
            name (str): Variable name

        Returns:
            Real name of variable or None if variable not found
        """
        if hasattr(cls, name):
            return name

        # get all variables
        variables = {}
        variables.update([(x.lower(), x) for x in cls.__dict__ if not x.startswith('__')
                          and not hasattr(cls.__dict__[x], '__call__')
                          and not hasattr(cls.__dict__[x], '__func__')])

        # check case insensitive variable
        if name.lower() in variables:
            return variables[name.lower()]
        else:
            # try to fix variable name
            cor_name = Tools.convert_name_to_variable(name).lower()
            if cor_name != name.lower() and cor_name in variables:
                logger, syslogger = getLoggers(__file__)
                logger.warning('Variable %s was corrected to %s' % (NAME.safe_substitute(name=name),
                                                                    NAME.safe_substitute(name=cor_name)), syslogger)
                return variables[name.lower()]
            else:
                return None

    @staticmethod
    def set_class_variable(cls, name, value, case, suite):
        """
        Setup class variable according to variable type

        Args:
            cls (class): Class for setup variable
            name (str): Variable name
            value (any): Variable value
            case (dict): TestCase dictionary
            suite (dict): Suite for error message, to add filter

        Function add TestSuite filter.

        Filters:
            - set_class_variable: When variable was added

        Raise:
            ParametersParseError: when variable cannot be set
            VariableFoundError: when variable not found
        """

        tmp = Params.get_variable_name(cls, name)
        if tmp is not None:
            name = tmp
            if name.startswith('__'):
                raise ParametersParseError('Private variable "%s" cannot be changed via parameters' % name)

            # get function name to add to TestSuite as filter
            filter_name = inspect.getframeinfo(inspect.currentframe()).function

            # variable from class
            real = getattr(cls, name)
            try:
                syslogger = getSysLogger()
                # check if it one of auto variables
                if not Params.set_auto_variable(cls, name, value, suite):
                    # Convert boolean if it in string
                    if isinstance(value, str) and isinstance(real, bool) and value.lower() in ['false', 'true']:
                        setattr(cls, name, ast.literal_eval(value.lower().capitalize()))
                    # Any value may be set to 'None'
                    elif value is None or isinstance(value, str) and value.lower() == 'none':
                        setattr(cls, name, None)
                    # 'None' value may receive any type from parameters
                    elif isinstance(real, type(None)):
                        setattr(cls, name, value)
                    # Assign only the same values
                    elif isinstance(real, type(value)):
                        setattr(cls, name, value)
                    else:
                        raise ValueError

                    # add applied filter to TestSuite
                    suite['filters'].append(filter_name)

                    # logging all changes
                    syslogger.info('SET variable (%s.%s.%s = %s)'
                                   % (SUITE_FULL.safe_substitute(case=case['name'], index=case['index'],
                                                                 suite=suite['name']), cls.__name__, name, value))
                else:
                    # logging all changes
                    syslogger.info('SET auto variable (%s.%s.%s = %s)'
                                   % (SUITE_FULL.safe_substitute(case=case['name'], index=case['index'],
                                                                 suite=suite['name']), cls.__name__, name, value))
            except ValueError:
                raise ParametersParseError('Inconsistent value type for "%s=%s" variable: expected - [%s], found - [%s]'
                                           % (name, value, type(real), type(value)))
        else:
            # check if it one of auto variables
            if not Params.set_auto_variable(cls, name, value, suite):
                raise VariableFoundError('Variable "%s" not found in %s Test Class of [%s.%s] TestSuite ! '
                                         % (name, cls.__name__, case['name'], suite['name'])
                                         + 'Use [--variable-list] options to print all available variables !')

    @staticmethod
    def set_suite_tests(tests, suite, case):
        """
        Configure all Tests according to selected

        Tests which starts with minus "-" should be excluded.
        Tests which starts with asterisk "*" should have sorted priority.

        Args:
             tests (list): Selected Tests
             suite (dict): TestSuite dictionary
             case (dict): TestCase dictionary

        Function add TestSuite filters.

        Filters:
            - set_suite_tests_include: When include option in use
            - set_suite_tests_exclude: When exclude option (minus symbol) in use
            - set_suite_tests_priority: When sort priority option (asterisk symbol) in use

        Raise:
            ParametersParseError: when error found in parameters
            TestNotFoundError: when selected Test not found
        """
        # get list of all Test function names
        test_names = [x['id'] for x in suite['tests']]
        # get list of all Test descriptions
        test_desc = [x['name'] if x['name'] is not None else None for x in suite['tests']]

        # get function name to add to TestSuite as filter
        filter_name = inspect.getframeinfo(inspect.currentframe()).function

        # check Tests
        include = None
        # Test order priority list
        test_order_priority = []
        # result Test list
        result_test_list = []
        for test in tests:
            if (test.startswith('-') and include is True) \
                    or (not test.startswith('-') and not test.startswith('*') and include is False):
                raise ParametersParseError('Inconsistent Test include parameters: Test cannot be '
                                           + 'included and excluded for %s TestSuite '
                                           % SUITE_FULL.safe_substitute(case=case['name'], index=case['index'],
                                                                        suite=suite['name'])
                                           + 'in same time !')
            # order current test
            order = False
            # exclude Test
            if test.startswith('-'):
                include = False
                # remove minus
                test = test[1:].strip()
            # order priority
            elif test.startswith('*'):
                # remove asterisk
                test = test[1:].strip()
                order = True
            else:
                include = True

            # check test
            if test.lower() in test_names:
                # add to order priority
                if order:
                    # ignore duplicates in order list
                    if suite['tests'][test_names.index(test.lower())] not in test_order_priority:
                        test_order_priority.append(copy.deepcopy(suite['tests'][test_names.index(test.lower())]))
                # add to test list
                else:
                    result_test_list.append(copy.deepcopy(suite['tests'][test_names.index(test.lower())]))
            elif test.lower() in test_desc:
                # if len([x for x in test_desc if x == test.lower()]) > 1:
                #     raise ParametersParseError('Test [%s] cannot be selected by second name ' % test
                #                                + 'for [%s.%s] TestSuite due to was ' % (case_name, suite['name'])
                #                                + 'found more one Test with this second name. '
                #                                + 'Please use Test function name to select this test '
                #                                + 'or correct name in TestSuite file !')
                # result_test_list.append(suite['tests'][test_desc.index(test.lower())])

                # select all test with same second name
                added = []
                for i, x in enumerate(test_desc):
                    if x == test.lower() and i not in added:
                        if order:
                            # ignore duplicates in order list
                            if suite['tests'][i] not in test_order_priority:
                                test_order_priority.append(copy.deepcopy(suite['tests'][i]))
                        else:
                            result_test_list.append(copy.deepcopy(suite['tests'][i]))
                        added.append(i)

                if len(added) > 1 and not order:
                    logger, syslogger = getLoggers(__file__)
                    logger.warning('%d Tests were selected for %s TestSuite by %s second Test name !'
                                   % (len(added), SUITE_FULL.safe_substitute(case=case['name'], index=case['index'],
                                                                             suite=suite['name']),
                                      NAME.safe_substitute(name=test)), syslogger)
            else:
                raise TestNotFoundError('Test %s not found in %s TestSuite ! '
                                        % (NAME.safe_substitute(name=test),
                                           SUITE_FULL.safe_substitute(case=case['name'], index=case['index'],
                                                                      suite=suite['name']))
                                        + 'Use [--test-list] option to print all available Tests.')

        # add included Tests only
        if include is True:
            suite['tests'] = tuple(result_test_list)
            suite['filters'].append(filter_name + '_include')
        elif include is False:
            tmp = []
            for test in suite['tests']:
                if test not in result_test_list:
                    tmp.append(test)

            # all Test were excluded
            if len(tmp) == 0:
                raise ParametersParseError('All Tests cannot be excluded from %s TestSuite !'
                                           % SUITE_FULL.safe_substitute(case=case['name'], index=case['index'],
                                                                        suite=suite['name']))
            suite['tests'] = copy.deepcopy(tmp)  # tuple(copy.deepcopy(tmp))
            # add applied filter to TestSuite
            suite['filters'].append(filter_name + '_exclude')

        # Tests sort priority
        if len(test_order_priority) > 0:
            # check errors in order
            for test in test_order_priority:
                if test not in suite['tests']:
                    raise ParametersParseError('Error of %s Test priority. Test was not included to launch list.'
                                               % NAME.safe_substitute(name=test['id']))
            # order Tests
            suite['tests'] = tuple(sorted(suite['tests'], key=lambda x: [test_order_priority.index(x)
                                                                         if x in test_order_priority
                                                                         else len(test_order_priority)]))
            # add applied filter to TestSuite
            suite['filters'].append(filter_name + '_priority')

        # update Test index
        for i, test in enumerate(suite['tests']):
            test['index'] = i+1

    @staticmethod
    async def filter_by_params(params_option):
        """
        Prepare TestCase launch and filter it by included TestSuites.
        Minus **-** symbol before TestSuite change filter behavior to exclude TestSuite.
        TestSuites set of each TestCases should be delimited by semicolon **;** in same order as TestCases.
        TestSuites inside set should be delimited by comma **,**.

        Example:
            --test "testCase1, testCase2" -p "-test01, variable=True"

        Args:
            params_option (str or None): String line of selected parameters

        Function add TestCase filter:

        Filters:
            - filter_by_params: When parameters were parse

        Raises:
            ParametersParseError: when error found in parameters
            TestNotFoundError: when selected Test not found in TestSuite
        """
        await Wait.wait_for_selected_suites()

        logger, syslogger = getLoggers(__file__)
        try:
            param_list = Tools.convert_str_params_to_list(params_option)
        except Exception as e:
            raise ParametersParseError('Parameters parse error: %s' % e)

        # TestSuites sets more than TestCases
        if len(param_list) > len(CONFIG.UNITTEST.SELECTED_TEST_CASES):
            raise ParametersParseError('Test parameters error: '
                                       + 'Count of sets of Test Parameters more than selected TestCases ! '
                                       + 'Use [--help] option to get help of options.')

        # fill list with None according to selected TestCases
        param_list += [None] * abs(len(param_list) - len(CONFIG.UNITTEST.SELECTED_TEST_CASES))

        # wait loading tests
        await Wait.wait_for_load_tests()

        # get function name to add to TestCases as filter
        filter_name = inspect.getframeinfo(inspect.currentframe()).function

        # stan cases
        for i, case in enumerate(CONFIG.UNITTEST.SELECTED_TEST_CASES):
            # current parameters
            params = param_list[i]

            # no changes without parameters
            if params is None:
                continue

            # all TestSuite names
            available_suites = [x['name'] for x in case['suites']]

            # split parameters by TestSuite selectors
            suite_selectors = [(x.lower().strip('#:'), j) for j, x in enumerate(params)
                               if str(x).startswith('#') and str(x).endswith(':')]

            # TestSuite selector missed when available TestSuites more one
            if len(suite_selectors) == 0:
                if len(available_suites) > 1:
                    raise ParametersParseError('TestSuite selector [#TEST_SUITE:] is required in parameters '
                                               + 'if available more one TestSuites ! '
                                               + 'Use [--suite-list] to print all available TestSuites')
                else:
                    # add selector for single TestSuite
                    suite_selectors.append((available_suites[0], 0))

            # check TestSuite selectors
            for j, x in enumerate(suite_selectors):
                # missing variables
                if j == 0 and x[1] != 0:
                    raise ParametersParseError('Variables %s specified before TestSuite selector [#TEST_SUITE:]'
                                               % params[:j + 1])
                # check TestSuite
                if x[0] not in available_suites:
                    raise ParametersParseError('TestSuite [%s] not found in [%s] TestCase !' % (x[0], case['name']))
                # check duplicates
                if x[0] in [x[0] for x in suite_selectors[j + 1:]]:
                    raise ParametersParseError('TestSuite [%s] selector was duplicated in parameters ' % x[0]
                                               + 'for [%s] TestCase !' % case['name'])

            # scan suites
            for j, selector in enumerate(suite_selectors):
                name, index = selector
                for suite in case['suites']:
                    if suite['name'] == name:
                        # get parameters for current selector
                        variables = param_list[i][index:] if len(suite_selectors[j+1:]) == 0 \
                            else param_list[i][index:suite_selectors[j+1][1]]

                        if len(variables) == 1 and variables[0] == '':
                            logger.waring('Parameters are missing for [%s] TestSuite selector !' % name, syslogger)

                        # set up parameters
                        tests = []
                        for k, var in enumerate(variables):
                            if isinstance(var, str) and var.startswith('#') and var.endswith(':'):
                                continue

                            # variable
                            if isinstance(var, tuple):
                                var_name, var_val = var
                                # probably it's Test name
                                if var_name is None:
                                    tests.append(str(var_val).strip())
                                else:
                                    # check duplicates for variables only. Test may be duplicated
                                    if var_name in [x[0] for x in variables[k+1:] if isinstance(x, tuple)]:
                                        raise ParametersParseError('Variable [%s] was duplicated ' % var_name
                                                                   + 'in parameters for [%s.%s] TestSuite !'
                                                                   % (case['name'], suite['name']))
                                    # setup variable
                                    cls = suite['class']
                                    # assign variable to class
                                    Params.set_class_variable(cls, name=var_name, value=var_val, case=case, suite=suite)
                            # Test name
                            else:
                                if var != '':
                                    tests.append(var)

                        # keep parameters in TestSuite
                        suite['params'] = Tools.variables_to_str(variables)

                        # add Tests to TestSuite
                        Params.set_suite_tests(tests, suite=suite, case=case)
                        break

            # add filter to TestCase
            case['filters'].append(filter_name)
