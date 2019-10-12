# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "11/01/17 12:33"

#: max length of test description
MAX_DOC_LINE_LENGTH = 200

#: cut line end. Increase length of doc line
CUT_LINE_SUFFIX = '...'

#: Filter names
FILTERS_NAMES = {'case_select': 'filter_by_cases',
                 'suite_select': 'filter_by_suite',
                 'test_load': 'load_tests',
                 'test_select': 'filter_by_params',
                 'set_variables': 'set_class_variable',
                 'set_tests_include': 'set_suite_tests_include',
                 'set_tests_exclude': 'set_suite_tests_exclude',
                 'set_tests_priority': 'set_suite_tests_priority'
                 }

#: Test time tag format
TEST_TIME_TAG_FORMAT = '%m.%d %H:%M:%S'

#: Unittest result delimiter 1
RESULT_DELIMITER_1 = '='
#: Unittest result delimiter 2
RESULT_DELIMITER_2 = '-'

#: Unittest result names
RESULT_NAMES = {'pass': 'PASS',
                'error': 'ERROR',
                'fail': 'FAIL',
                'skip': 'SKIP',
                'not run': 'NOT RUN',
                'interrupt': 'NOT RUN',
                'excepted': 'EXPECTED FAILURE',
                'unexpected': 'UNEXPECTED SUCCESS'}
