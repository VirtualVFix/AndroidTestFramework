# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/22/18 15:40"


class UiSettingsError(Exception):
    """
    Device shell utilities base exception class.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DateTimeFormatError(UiSettingsError):
    def __init__(self, value):
        super(DateTimeFormatError, self).__init__(value)


class JUnitRunnerError(UiSettingsError):
    def __init__(self, value):
        super(JUnitRunnerError, self).__init__(value)


class ConsentDialogError(UiSettingsError):
    def __init__(self, value):
        super(ConsentDialogError, self).__init__(value)


class DebugSetingsError(UiSettingsError):
    def __init__(self, value):
        super(DebugSetingsError, self).__init__(value)


class DisplaySetingsError(UiSettingsError):
    def __init__(self, value):
        super(DisplaySetingsError, self).__init__(value)


class SecuritySetingsError(UiSettingsError):
    def __init__(self, value):
        super(SecuritySetingsError, self).__init__(value)


class WirelessSetingsError(UiSettingsError):
    def __init__(self, value):
        super(WirelessSetingsError, self).__init__(value)


class TrafficError(UiSettingsError):
    def __init__(self, value):
        super(TrafficError, self).__init__(value)


class SetupWizardError(UiSettingsError):
    def __init__(self, value):
        super(SetupWizardError, self).__init__(value)
