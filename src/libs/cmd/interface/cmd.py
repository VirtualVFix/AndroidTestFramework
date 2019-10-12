# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/22/17 14:28"

from abc import ABCMeta, abstractmethod


class Cmd(metaclass=ABCMeta):
    """
    Class to work with PC console.
    """

    @abstractmethod
    def __init__(self, logger=None, **kwargs):
        """
        Args:
            logger (logging): Custom logger if need output with one logger. New logger will be created if None. (Default: None)
        """

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """
        Should execute any string command
        """
