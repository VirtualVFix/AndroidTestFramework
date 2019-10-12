# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "10/16/17 14:24"

from libs.core.options.exceptions import OptionsError


class LauncherError(Exception):
    """
    Base launcher exception class.
    """
    def __init__(self, value=''):
        self.value = value

    def __str__(self):
        return repr(self.value)


class PrepareLauncherError(LauncherError):
    def __init__(self, value=''):
        super(PrepareLauncherError, self).__init__(value)


class InterruptByUser(LauncherError):
    def __init__(self, value=''):
        super(InterruptByUser, self).__init__(value)


class InterruptByError(LauncherError):
    def __init__(self, value=''):
        super(InterruptByError, self).__init__(value)


class InterruptByFail(LauncherError):
    def __init__(self, value=''):
        super(InterruptByFail, self).__init__(value)


class RuntimeInterruptError(LauncherError):
    """
    Silent stop Framework with display one line error message.
    """
    def __init__(self, value=''):
        super(RuntimeInterruptError, self).__init__(value)