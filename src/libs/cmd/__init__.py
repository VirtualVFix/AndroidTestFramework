# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/19/17 14:52"
__doc__ = """
This module allow work with PC terminal ``cmd``, ``adb`` and ``fastboot`` utilities:

    * ``adb`` utility allow to work with device in Idle state and device ``shell`` if **ADB debug** is enable.
    * ``fastboot`` utility allow to work with device in bootloader state.
    * ``cmd`` PC terminal allow execute any terminal command depends of OS.
"""


from libs.cmd.manager import Manager
from libs.cmd.implement.base.cmd import Cmd
from libs.cmd.implement.base.adb import Adb
from libs.cmd.implement.base.shell import Shell
from libs.cmd.implement.base.command import Command
from libs.cmd.implement.base.fastboot import Fastboot

__all__ = ['Cmd', 'Manager', 'Fastboot', 'Adb', 'Shell', 'Command']
