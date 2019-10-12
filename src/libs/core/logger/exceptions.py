# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/27/17 15:06"


class LoggerError(Exception):
    """
    Base logger exception class.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class TableError(LoggerError):
    """
    Table base error.
    """
    def __init__(self, value):
        super(TableError, self).__init__(value)


class TableSizeError(TableError):
    """
    Table size error.
    """
    def __init__(self, value):
        super(TableSizeError, self).__init__(value)


class TableFormatError(TableError):
    """
    Table size error.
    """
    def __init__(self, value):
        super(TableFormatError, self).__init__(value)
