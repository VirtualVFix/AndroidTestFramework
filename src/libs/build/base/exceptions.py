# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/26/18 15:29"


class FlashError(Exception):
    """
    Device flash base exception class.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BuildNotFoundError(FlashError):
    def __init__(self, value):
        super(BuildNotFoundError, self).__init__(value)


class BuildUnpackError(FlashError):
    def __init__(self, value):
        super(BuildUnpackError, self).__init__(value)


class BuildDownloadError(FlashError):
    def __init__(self, value):
        super(BuildDownloadError, self).__init__(value)
