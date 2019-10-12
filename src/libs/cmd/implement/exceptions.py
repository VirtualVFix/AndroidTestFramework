# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/22/17 14:23"


class CmdError(Exception):
    """
    Base CMD exception class.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class PropertyError(CmdError):
    def __init__(self, value):
        super(PropertyError, self).__init__(value)


class ImplementationNotFoundError(CmdError):
    def __init__(self, value):
        super(ImplementationNotFoundError, self).__init__(value)


# Command execution errors
class CommandExecuteError(CmdError):
    def __init__(self, value):
        super(CommandExecuteError, self).__init__(value)


class ResultError(CommandExecuteError):
    def __init__(self, value):
        super(ResultError, self).__init__(value)


class TimeoutExpiredError(CommandExecuteError):
    def __init__(self, value):
        super(TimeoutExpiredError, self).__init__(value)


class CommandNotFoundError(CommandExecuteError):
    def __init__(self, value):
        super(CommandNotFoundError, self).__init__(value)


class AccessDeniedError(CommandExecuteError):
    def __init__(self, value):
        super(AccessDeniedError, self).__init__(value)


class ObjectDoesNotExistError(CommandExecuteError):
    def __init__(self, value):
        super(ObjectDoesNotExistError, self).__init__(value)


class RemountFailedError(CommandExecuteError):
    def __init__(self, value):
        super(RemountFailedError, self).__init__(value)


class DeviceEnumeratedError(CommandExecuteError):
    def __init__(self, value):
        super(DeviceEnumeratedError, self).__init__(value)


class MoreOneDeviceError(DeviceEnumeratedError):
    def __init__(self, value):
        super(MoreOneDeviceError, self).__init__(value)


class AdbInternalError(CommandExecuteError):
    def __init__(self, value):
        super(AdbInternalError, self).__init__(value)


class CommandSyntaxError(CommandExecuteError):
    def __init__(self, value):
        super(CommandSyntaxError, self).__init__(value)


# class DeviceNotFoundError(CommandExecuteError):
#     def __init__(self, value):
#         super(DeviceNotFoundError, self).__init__(value)


class InconsistentStateError(CommandExecuteError):
    def __init__(self, value):
        super(InconsistentStateError, self).__init__(value)
