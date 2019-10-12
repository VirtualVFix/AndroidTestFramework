# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "10/26/17 16:51"

import re
import os
import asyncio
import inspect
from config import CONFIG
from unittest import TestCase
from libs.core.tools import load_module
from libs.core.unittest.exceptions import TestSuiteLoadError
from libs.core.logger import getLogger, getSysLogger
from libs.core.unittest.config import MAX_DOC_LINE_LENGTH, CUT_LINE_SUFFIX
from libs.core.template import NAME, CASE_WITH_PATH, SUITE


class ScanCases:
    """
    Scan project to find all available TestCases with TestSuites
    """

    def __init__(self, logger=None):
        self.logger = logger or getLogger(__file__)
        self.syslogger = getSysLogger()

    @staticmethod
    def cut_long_doc_line(doc):
        """
        Cut long documentation line depends of MAX_DOC_LINE_LENGTH config parameter.

        Args:
            doc (str): Documentation line

        Returns:
            doc (str): Doc line with length no more (MAX_DOC_LINE_LENGTH + len(CUT_LINE_SUFFIX))
        """
        if doc is None:
            return None

        tmp = ''
        # cat long doc line
        if len(doc) > MAX_DOC_LINE_LENGTH:
            for i, x in enumerate(doc.split(' ')):
                if len(tmp + x) < MAX_DOC_LINE_LENGTH:
                    if i > 0:
                        tmp += ' '
                    tmp += x
                else:
                    break
            if len(tmp) == 0:
                tmp = doc[:MAX_DOC_LINE_LENGTH]
            return tmp + CUT_LINE_SUFFIX
        return doc

    async def scan(self):
        """
        Scan project to find unittests.

        Getting all available TestCases with TestSuites and packing all to **CONFIG.UNITTEST.AVAILABLE_TEST_CASES**
        config variable.

        More details about config variable structure may be found in :func:`generate_cases_dict`
        """
        # get tests async generator
        cases = await self.get_cases()

        # generate case list with suites
        tmp = await self.generate_cases_dict(cases)
        cases = {}
        for key in tmp:
            if len(tmp[key]['suites']) == 0:
                self.logger.error('%s TestCase will be ignored due to no one TestSuite found !'
                                  % CASE_WITH_PATH.safe_substitute(case=key, path=tmp[key]['path']), self.syslogger)
                if CONFIG.SYSTEM.DEBUG:
                    raise TestSuiteLoadError(self.logger.lastmsg())
            else:
                cases[key] = tmp[key]
        del tmp

        #: Keep all available test cases in config
        CONFIG.UNITTEST.AVAILABLE_TEST_CASES = cases
        CONFIG.UNITTEST.LOCK('AVAILABLE_TEST_CASES')

    async def generate_cases_dict(self, async_cases) -> dict:
        """
        Generate case dict.

        Args:
            async_cases (async generator): Test cases generator

        Returns:
            dict: TestCase dictionary with TestSuites

        Dictionary structure:

        .. code-block:: python

            {'case': {
                'name': 'TestCase name',           # TestCase name with point "." as path separator
                'doc': 'Doc line',                 # Documentation line (module description) from __init__.py module (.py only)
                'path': 'path',                    # Full path to module
                'index': int,                      # TestCase index for launch. Used to identify duplicates TestCases. Starting from 1
                'filters': [],                     # Filter list witch was apply to TestCase

                # list of TestSuite dictionaries
                'suites': [{
                    'name': 'SuiteName',           # TestSuite name
                    'doc': 'Doc line',             # TestSuite documentation line from __doc__ module tag
                    'path': 'path',                # Full path to TestSuite module
                    'class': __class__,            # Loaded tests class implemented from unittest.TestCase
                    'filters': [],                 # Filter list witch was apply to TestSuite
                    'params': 'parameters option', # TestSuite additional parameters specified in parameter option
                    'ran': 0,                      # How many Tests were ran
                    'tests': []                    # List of Tests dicts. Empty on this step
                    }]
                }
            }

        Details of **tests** structure may be found in :func:`ScanTests.load_tests` function
        """
        cases = {}
        # create case dict
        async for case in async_cases:
            case_name, case_doc, case_path, suite_name, suite_path = case
            if case_name not in cases:
                cases[case_name] = {
                    'name': case_name,
                    'doc': self.cut_long_doc_line(case_doc),
                    'path': case_path,
                    'index': -1,
                    'filters': [],
                    'suites': [],
                    'suite.list': []
                }
            # load test classes from TestSuite
            suite_cls, suite_doc = await self.get_suite_class_and_doc(case)
            if suite_cls is not None:
                suite = {'name': suite_name,
                         'path': suite_path,
                         'doc': self.cut_long_doc_line(suite_doc),
                         'class': suite_cls,
                         'filters': [],
                         'params': None,
                         'ran': 0,
                         'tests': []}
                cases[case_name]['suites'].append(suite)
            await asyncio.sleep(0)

        # sorted TestSuites by name
        for case in cases:
            cases[case]['suites'] = sorted(cases[case]['suites'], key=lambda x: x['name'])

        return cases

    async def get_suite_class_and_doc(self, case, module=None):
        """
        Load potential unittest module and find unittest.TestCase classes,
        also load test description from module doc line.

        Args:
            case (tuple): (TestCase name, TestCase doc, TestCase path, TestSuite name, TestSuite path)
            module (str): Special module name to loaded class and class functions.
            Required when class reloaded from module.

        Raises:
            TestSuiteLoadError is module cannot be loaded

        Returns:
            str, class: Doc line or None and unittest.TestCase class from TestSuite module
        """
        case_name, _, case_path, suite_name, suite_path = case
        self.syslogger.info('Loading TestSuite %s from %s TestCase'
                            % (NAME.safe_substitute(name=suite_name),
                               CASE_WITH_PATH.safe_substitute(case=case_name, path=case_path)))

        mod, doc = None, None
        try:
            mod = load_module('scansuite_%s' % suite_name, suite_path)
            doc = mod.__doc__.strip('\n') if mod.__doc__ is not None else None
        except Exception as er:
            self.syslogger.exception(er)
            if CONFIG.SYSTEM.DEBUG:
                self.logger.error('TestSuite %s from %s TestCase cannot be loaded due to %s: %s'
                                  % (NAME.safe_substitute(name=suite_name),
                                     CASE_WITH_PATH.safe_substitute(case=case_name, path=case_path),
                                     er.__class__.__name__, er))
        result = []
        if mod is not None:
            # scan module and find unittest classes
            for name, cls in inspect.getmembers(mod):
                if inspect.isclass(cls) and issubclass(cls, TestCase):
                    self.syslogger.info('Found %s class' % NAME.safe_substitute(name=cls.__name__))
                    # change module name for class and functions inside if required
                    if module is not None:
                        cls.__module__ = module
                        self.syslogger.info('Module of %s class was changed to %s'
                                            % (NAME.safe_substitute(name=cls.__name__),
                                               NAME.safe_substitute(name=cls.__module__)))
                        for _name, obj in inspect.getmembers(cls):
                            if inspect.isfunction(obj) and obj.__module__ == 'scansuite_%s' % suite_name:
                                obj.__module__ = '%s.%s' % (module, suite_name)
                                self.syslogger.info('Module of %s class function was changed to %s'
                                                    % (SUITE.safe_substitute(case=cls.__name__, suite=_name),
                                                       NAME.safe_substitute(name=obj.__module__)))
                    result.append(cls)

            # check issues
            if len(result) == 0:
                self.syslogger.error('No one test class was found in %s TestSuite !'
                                    % (SUITE.safe_substitute(case=case_name, suite=suite_name)))
                if CONFIG.SYSTEM.DEBUG:
                    self.logger.error(self.syslogger.lastmsg())
            elif len(result) > 1:
                result = sorted(result, key=lambda x: x.__name__)
                self.syslogger.error('Multiple test classes are found in %s TestSuite '
                                     % NAME.safe_substitute(name=suite_name)
                                     + 'from %s TestCase ! '
                                     % CASE_WITH_PATH.safe_substitute(case=case_name, path=case_path)
                                     + 'Multiple test classes are not supported, so '
                                     + '%s class was selected to run according '
                                     % NAME.safe_substitute(name=result[0].__name__)
                                     + 'to name sorting priority. All other test classes were ignored.')
                if CONFIG.SYSTEM.DEBUG:
                    self.logger.error(self.syslogger.lastmsg())
            del mod
            self.syslogger.done()
        else:
            self.syslogger.error('Module not found !')
        return result[0] if len(result) > 0 else None, doc

    async def get_cases(self):
        """
        Scan project to find unittests in tests folder if CONFIG.UNITTEST.SELF_TEST == false and in libs folder
        otherwise.

        Uses :func:`get_potentials_tests` to get tests depends of CONFIG.UNITTEST.SELF_TEST parameter.

        Returns:
            asynchronous generator (TestCase name, TestCase doc, TestCase path, TestSuite name, TestSuite path):
            async generator of tuples with TestCase name, full path to TestCase, TestCase documentation,
            TestSuite name and full path to TestSuite
        """
        self.logger.info('Search for tests...')
        if CONFIG.UNITTEST.SELF_TEST is True:
            # scan all project
            result = self.get_potential_cases(CONFIG.SYSTEM.ROOT_DIR, (CONFIG.PROJECT_SELFTEST_FOLDER,))
        else:
            # scan tests
            result = self.get_potential_cases(CONFIG.PROJECT_TESTS_FOLDER, (CONFIG.PROJECT_TESTS_SUITE_FOLDER,))
        self.logger.done()
        return result

    @staticmethod
    async def get_potential_cases(root_folder_name, test_folders):
        """
        Get all potentials TestCases with TestSuites.

        Args:
            root_folder_name (str): Name of root dir in `CONFIG.SYSTEM.ROOT_DIR` folder
            test_folders (tuple): Names of folders with potentials TestSuites

        Returns:
            asynchronous generator (TestCase name, TestCase doc, TestCase path, TestSuite name, TestSuite path):
            async generator of tuples with TestCase name, full path to TestCase, TestCase documentation,
            TestSuite name and full path to TestSuite
        """
        root_dir = os.path.join(CONFIG.SYSTEM.ROOT_DIR, root_folder_name)
        for root, _, files in os.walk(root_dir):
            if root.endswith(tuple(os.sep + x for x in test_folders)):
                for file in sorted(files):
                    if file.endswith(CONFIG.PROJECT_FILE_EXTENSIONS) and not file.startswith('_'):
                        # get test name
                        name = root[len(os.path.join(CONFIG.SYSTEM.ROOT_DIR, root_folder_name)):]
                        # cut test folders
                        for x in range(2):
                            if name.endswith(test_folders):
                                name = os.path.split(name)[0]
                            else:
                                break

                        mod_path = os.path.join(os.path.join(CONFIG.SYSTEM.ROOT_DIR, root_folder_name), name[1:])

                        doc = None
                        # try to loading module documentation
                        init = os.path.join(mod_path, '__init__.py')
                        if os.path.exists(init):
                            with open(init, 'r') as read:
                                match = re.search('__doc__\s*=\s*(\'|")(.*?)(\'|")\n', read.read(), re.I|re.M)
                                if match:
                                    doc = match.group(2)
                        # async generator (\/).'_'.(\/) because I can ... make life complicated
                        # return tuple
                        yield (name.replace(os.sep, '.')[1:].lower(),                    # TestCase name
                               doc,                                                      # TestCase doc
                               mod_path,                                                 # TestCase path
                               '.'.join(x for x in file.split('.') if '.' + x
                                        not in CONFIG.PROJECT_FILE_EXTENSIONS).lower(),  # TestSuite name
                               os.path.join(root, file))                                 # TestSuite path
