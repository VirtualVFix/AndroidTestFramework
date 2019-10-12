# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/22/18 15:40"


class UtilityError(Exception):
    """
    Device shell utilities base exception class.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class PathOnDeviceNotFoundError(UtilityError):
    def __init__(self, value):
        super(PathOnDeviceNotFoundError, self).__init__(value)


class SyncDateError(UtilityError):
    def __init__(self, value):
        super(SyncDateError, self).__init__(value)
        

class DeviceLoggingError(UtilityError):
    def __init__(self, value):
        super(DeviceLoggingError, self).__init__(value)


class LifeNetworkError(UtilityError):
    def __init__(self, value):
        super(LifeNetworkError, self).__init__(value)


class PowerUpReasonError(UtilityError):
    def __init__(self, value):
        super(PowerUpReasonError, self).__init__(value)
