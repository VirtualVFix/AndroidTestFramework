# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/27/17 15:06"


class UnitTestError(Exception):
    """
    Base unittests exception class.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class TestSuiteOptionsError(UnitTestError):
    def __init__(self, value=''):
        super(TestSuiteOptionsError, self).__init__(value)


class TestSuiteNotFoundError(UnitTestError):
    def __init__(self, value=''):
        super(TestSuiteNotFoundError, self).__init__(value)


class TestCaseNotFoundError(UnitTestError):
    def __init__(self, value=''):
        super(TestCaseNotFoundError, self).__init__(value)


class TestNotFoundError(UnitTestError):
    def __init__(self, value=''):
        super(TestNotFoundError, self).__init__(value)


class ParametersParseError(UnitTestError):
    def __init__(self, value=''):
        super(ParametersParseError, self).__init__(value)


class VariableFoundError(UnitTestError):
    def __init__(self, value=''):
        super(VariableFoundError, self).__init__(value)


class VariableParseError(UnitTestError):
    def __init__(self, value=''):
        super(VariableParseError, self).__init__(value)


class TestSuiteLoadError(UnitTestError):
    def __init__(self, value=''):
        super(TestSuiteLoadError, self).__init__(value)


class TestSuiteLaunchError(UnitTestError):
    def __init__(self, value=''):
        super(TestSuiteLaunchError, self).__init__(value)