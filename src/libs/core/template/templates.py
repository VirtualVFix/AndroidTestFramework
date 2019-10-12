# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "12/11/2017 2:34 PM"

"""
Template messages for Framework core notifications 
"""

from string import Template

#: TestCase with index
CASE = Template('[$case/#$index]')
#: Name of TestSuite with TestCase and TestCase index.
SUITE_FULL = Template('[$case.$suite/#$index]')
#: Name of TestSuite with TestCase
SUITE = Template('[$case.$suite]')
#: TestCase with path
CASE_WITH_PATH = Template('[$case] <$path>')
#: Default shielding
NAME = Template('[$name]')
#: Default shielding
PARAMS = NAME  # Template('"$name"')
#: Test start short info
TEST_START = Template('$date $name$second ($desc)')
#: Test done short info
TEST_DONE = Template('$date $result [$rate%] ($time) $name$second ($desc)')
#: Test error info
TEST_ERROR = Template('$test / #$index')
