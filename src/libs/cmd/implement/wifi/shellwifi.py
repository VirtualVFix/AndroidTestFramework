# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/22/17 14:23"

from libs.cmd.implement.base.base import Base
from libs.core.tools import NotImplemented
from libs.cmd.interface.shell import Shell as ShellImp


@NotImplemented
class ShellWifi(Base, ShellImp):
    """
    Class to work with ``adb shell`` utility.

    See also:
        :mod:`src.libs.cmd.adb` module
    """

    def __init__(self, logger=None, serial=None, **kwargs):
        """
        Args:
            logger (logging): Custom logger if need output with one logger. New logger will be created if None. (Default: None)
            serial (str): Serial number of device. May be None (Default: None)
        """
        super(ShellWifi, self).__init__(logger=logger, serial=serial, **kwargs)

    def __call__(self, *args, **kwargs):
        """
        Call class as ``self.shell`` function

        Returns:
            func:
            self.shell(`*args`, `**kwargs`)
        """
        return self.shell(*args, **kwargs)
