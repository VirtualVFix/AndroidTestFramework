# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "10/16/17 14:24"


class OptionsError(Exception):
    """
    Base options parser exception class.
    """
    def __init__(self, value=''):
        self.value = value

    def __str__(self):
        return repr(self.value)


class OptionsParserError(OptionsError):
    def __init__(self, value=''):
        super(OptionsParserError, self).__init__(value)


class OptionsGroupParserError(OptionsError):
    def __init__(self, value=''):
        super(OptionsGroupParserError, self).__init__(value)


class OptionsValidationError(OptionsError):
    def __init__(self, value=''):
        super(OptionsValidationError, self).__init__(value)
