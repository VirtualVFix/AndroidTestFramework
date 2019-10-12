# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/22/17 14:23"


from .cmd import Cmd
from libs.cmd.implement.base.shell import Shell
from libs.cmd.implement.base.cmd import Cmd as CmdBase

#: Replace :class:`implement.base.cmd.Cmd` class by :class:`implement.emulator.cmd.Cmd`
#: After class replace Shell emulator class have same signature as Shell base
Shell.__bases__ = tuple([x if not issubclass(x, CmdBase) else Cmd for x in Shell.__bases__])
