# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/22/18 15:40"


class InstallError(Exception):
    """
    Install exception base class.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ApkNotFoundError(InstallError):
    def __init__(self, value):
        super(ApkNotFoundError, self).__init__(value)
