# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "11/08/17 15:17"

import os
import re
import ast
from config import CONFIG
from libs.core.logger import getLoggers, getSysLogger
from .exceptions import UnitTestError, TestSuiteNotFoundError, VariableParseError


class Tools:
    """
    Unittest helper tools
    """
    @staticmethod
    def variables_to_str(variables):
        """
        Convert variables list to string. Uses to print parameters in Test info.

        Args:
            variables (list): List of variables or None

        Returns:
             str or None
        """
        if variables is None:
            return None

        result = ''
        for x in variables:
            if isinstance(x, str):
                if x.strip().startswith('#'):
                    continue
                result += x
            elif isinstance(x, tuple):
                if x[0] is None:
                    if x[0].strip().startswith('#'):
                        continue
                    result += str(x[1]).strip() if not str(x[1]).strip().startswith('#') else ''
                else:
                    result += '%s=%s' % (x[0], x[1])
            result += ', '
        return result[:-2]

    @staticmethod
    def convert_name_to_variable(name, variable=None):
        """
        Concatenate name with variable via '_' symbol if variable is not None and convert it to correct variable name.

        Args:
             name (str): Any text which need to convert
             variable (str): Variable name for concatenate if not None

        Example:
            convert_name_to_variable('3dmark', 'cycles') returns '_3dmark_cycles'

        Returns:
            str: Correct variable name
        """
        _name = re.sub('[^\w\d_]+', '', str(name))
        _var = ('_' + re.sub('[^\w\d_]+', '', str(variable))) if variable is not None else ''
        return '%s%s' % (_name if not _name[0].isdigit() else ('_' + _name), _var)

    @staticmethod
    def get_default_suite_list(case) -> list:
        """
        Get default suite.list from TestCase and make verification of all TestSuites from list.
        suite.list file is options and may contain default TestSuites from TestCase to launch by default without
        specify TestSuites in option.

        Args:
            case (dict): TestCase dict (:func:`ScanCases.generate_cases_dict`)

        Returns:
            list: Names of validated TestSuite names or empty list if suite.list empty or N/A

        Raise:
            TestSuiteNotFoundError in DEBUG mode when TestSuite from suite.list file not found.
        """
        logger, syslogger = getLoggers(__file__)
        result = []

        list_path = os.path.join(case['path'], CONFIG.PROJECT_SUITE_LIST_FILE_NAME)
        if not os.path.exists(list_path):
            syslogger.warning('[%s] is not set for "%s" TestCase !'
                              % (CONFIG.PROJECT_SUITE_LIST_FILE_NAME, case['name']))
        else:
            with open(list_path) as file:
                tmp = [x.strip().strip('.py').lower()
                       for x in re.sub('[\r\t]*', '', file.read(), re.DOTALL).split('\n')]

                suite_names = [x['name'] for x in case['suites']]
                for x in tmp:
                    if x not in suite_names:
                        logger.error('TestSuite [%s] from %s not found for [%s] TestCase !'
                                     % (x, CONFIG.PROJECT_SUITE_LIST_FILE_NAME, case['name']), syslogger)
                        if CONFIG.SYSTEM.DEBUG:
                            raise TestSuiteNotFoundError(logger.lastmsg())
                    else:
                        result.append(x)
        return result

    @staticmethod
    def convert_str_cases_to_list(case_option):
        """
        Convert string TestCases option (--tests) to list

        Args:
            case_option (str): TestCases option as string

        Returns:
             list: list of TestCase names or empty list
        """
        return [x.lower().strip() for x in case_option.strip('"').split(',')
                if x.strip() != ''] if case_option is not None else []

    @staticmethod
    def convert_str_suites_to_list(suite_option):
        """
        Convert string TestSuite select option (--include / --exclude) to list.

        Args:
            suite_option (str): TestSuite select option as string

        Returns:
             list: list os TestSuite names or empty list
        """
        if suite_option is None:
            return []

        # split by cases
        tmp = [x.lower().strip() if x.strip() != '' else None for x in suite_option.strip('"').split(';')]
        summary = []
        for sub in tmp:
            summary.append(sub if sub is None else [x.lower().strip() if not x.endswith('.py')
                                                    else x.lower().strip()[:-3]
                                                    for x in sub.split(',') if x.strip() != ''])
        # cut last empty records
        for x in reversed(summary):
            if x is None:
                summary.pop()
            else:
                break
        return summary

    @staticmethod
    def convert_str_params_to_list(params_option):
        """
        Convert string TestParameters option (--parameters) to list with parsed variables.

        Supported the following variables types:
            - dict
            - tuple
            - list
            - str
            - int
            - float
            - composite variables with types above

        Args:
            params_option (str): TestParameters option as string

        Exception:
            VariableParseError when variable cannot be parsed

        Returns:
             list: list of TestParameters variables or empty list
        """
        if params_option is None:
            return []

        def is_all_nodes_closed(node_list):
            """ Check if all tags closed """
            nodes = {'dict': [], 'list': [], 'str': [], 'tuple': []}
            for j, keys in enumerate(node_list):
                node, start = keys
                # start node
                if start is True:
                    # skip node inside string
                    if len(nodes['str']) > 0:
                        continue
                    nodes[node].append(j)
                # close node
                elif start is False:
                    if len(nodes['str']) > 0:
                        continue
                    if len(nodes[node]) == 0:
                        return False
                    nodes[node].pop()
                # string
                else:
                    # string open
                    if len(nodes[node]) == 0:
                        nodes[node].append(j)
                    # string closed
                    else:
                        nodes[node].pop()
            return False not in [True if len(nodes[x]) == 0 else False for x in nodes]

        # split by cases
        params = [params_option.strip('"').strip()]
        summary = []
        k = 0
        while k < len(params):
            sub = params[k]
            # if sub in [None, '']:
            #     summary.append(None)
            #     continue

            result = []
            var = None
            cur = ''
            tags = []  # tags/node order list

            # split parameters by symbols
            for i, x in enumerate(sub):
                cur += x
                # dict tag
                if x == '{':
                    tags.append(('dict', True))  # open tag
                elif x == '}':
                    tags.append(('dict', False))  # close tag
                # str tag
                elif x in ('\'', '"'):
                    tags.append(('str', None))
                # list tag
                elif x == '[':
                    tags.append(('list', True))
                elif x == ']':
                    tags.append(('list', False))
                # tuple tag
                elif x == '(':
                    tags.append(('tuple', True))
                elif x == ')':
                    tags.append(('tuple', False))
                # find variable with value
                elif x == '=':
                    if len(tags) != 0:
                        raise SyntaxError('SyntaxError(\'unexpected EOF while parsing\', (%s))' % cur)
                    var = cur[:-1].strip()
                    cur = ''
                elif x == ':':
                    # find TestSuite selector end
                    if len(tags) == 0:
                        # add suite name
                        result.append(cur.strip())
                        cur = ''
                # elif x == '#':
                #     # find start of TestSuite selector
                #     if len(tags) == 0 and len(cur) > 1:
                #         # add previous value
                #         result.append(cur[:-1].strip())
                #         cur = x

                # find variable delimiter or end of line
                if x == ',' or x == ';' or i == len(sub)-1:
                    node_closed = False

                    if len(tags) == 0:
                        if var is None:
                            # test name
                            result.append(cur.strip().rstrip(',').rstrip(';'))
                        else:
                            # regular variable with value
                            try:
                                # make safety eval
                                cur = ast.literal_eval(cur.strip().rstrip(',').rstrip(';'))
                                result.append((var, cur))
                            except:
                                # add as string
                                result.append((var, cur.strip().rstrip(',').rstrip(';')))

                        cur = ''
                        var = None
                    # subscriptable variable
                    else:
                        node_closed = is_all_nodes_closed(tags)
                        if i == len(sub)-1 or node_closed is True:
                            try:
                                # make safety eval
                                cur = ast.literal_eval(cur.strip().rstrip(',').rstrip(';'))
                                result.append((var, cur))
                                cur = ''
                                var = None
                                tags = []
                            except Exception as e:
                                syslogger = getSysLogger()
                                syslogger.exception(e)
                                raise VariableParseError(e)

                    # find variables for new TestCase
                    if x == ';' and (len(tags) == 0 or node_closed is True):
                        params.append(params[k][i + 1:])
                        params[k] = params[k][:i]
                        break
            k += 1
            summary.append(result if len(result) > 0 and len([True for x in result if x == '']) < len(result) else None)

        # cut last None records
        for x in reversed(summary):
            if x is None:
                summary.pop()
            else:
                break
        return summary

    @staticmethod
    def get_class_variables(cls, cls_path):
        """
        Get all static variables from .py file and static variables from loaded class.
        Parse from .py variable name, variable value and comment if available.
        Used to get variable list of TestSuite.

        Args:
            cls (class): Loaded class
            cls_path (str): Full path to class file

        Returns:
            tuple([(name, value, comment), ...], [name, ...]): Variable list with comments from file and variable
            list of names from class
        """
        if not os.path.exists(cls_path):
            raise UnitTestError('"%s" TestSuite file not found !' % cls_path)

        var, real = [], []
        with open(cls_path, 'r+') as file:
            match = re.search('^class\s+' + cls.__name__ + '\s*\(.*?\)\s*\:[\r\t\n]+(.*?)(^@|def\s)+',
                              re.sub('[\r\t]+', '', file.read()), re.I|re.M|re.DOTALL)
            if match:
                var = [(x.strip(), y.strip(), z.replace('#', '').strip()) for x,y,z
                       in re.findall('^\s+([\w\d_-]+)\s*=\s*(.*?)(#.*?$|$)', match.group(1), re.I|re.M|re.DOTALL)]

        # load all variable from class
        real = [x for x in cls.__dict__ if not x.startswith('__')
                and not hasattr(cls.__dict__[x], '__call__')
                and not hasattr(cls.__dict__[x], '__func__')]
        return var, real
