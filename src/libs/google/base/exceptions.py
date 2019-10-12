# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/23/18 12:57"


class GoogleAPIError(Exception):
    """
    Google API base exception class.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SpreadsheetError(GoogleAPIError):
    def __init__(self, value):
        super(SpreadsheetError, self).__init__(value)


class SpreadsheetResultError(SpreadsheetError):
    def __init__(self, value):
        super(SpreadsheetResultError, self).__init__(value)
