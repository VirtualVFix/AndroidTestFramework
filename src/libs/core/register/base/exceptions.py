# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/27/17 15:06"


class ConfigError(Exception):
    """
    Config base exception.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ConfigAccessError(ConfigError):
    def __init__(self, value):
        super(ConfigAccessError, self).__init__(value)
