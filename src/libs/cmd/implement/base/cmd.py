# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/22/17 14:28"

import platform
from .base import Base
from libs.cmd.interface.cmd import Cmd as CmdImp
from libs.cmd.implement.base.command import Command


class Cmd(Base, CmdImp):
    """
    Class to work with PC console.
    """

    def __init__(self, logger=None, **kwargs):
        """
        Args:
            logger (logging, default None): Custom logger if need output with one logger.
                New logger will be created if None.
        """
        super(Cmd, self).__init__(logger=logger, **kwargs)

        self.logger = logger
        # keep last executed command
        self.__command = None

    @property
    def command(self):
        """
        Get last execute command property

        Returns:
             :class:`.command.Command` class or None
        """
        return self.__command

    def __call__(self, command, *args, **kwargs):
        """
        Should execute any command

        Args:
            command (str): String command to execute
        """
        if 'windows' in platform.system().lower():
            cmd = 'cmd /c %s' % command
        else:
            cmd = command

        kwargs = self.update_base_kwargs(**kwargs)

        # keep last executed command
        self.__command = Command(logger=self.logger)
        return self.__command.execute(command=cmd, **kwargs)
