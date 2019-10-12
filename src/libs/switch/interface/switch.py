# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/22/18 11:27"

from abc import ABCMeta, abstractmethod


class Switch(metaclass=ABCMeta):
    """ Abstract class for switchboard """

    @abstractmethod
    def __init__(self, serial, logger=None, **kwargs):
        """
        Args:
            serial (str): Serial number of switchboard
            logger (logging, default None): Custom logger if need output with one logger.
                New logger should be created if None
        """
        pass

    def switch_to_charging_mode(self, *args, **kwargs):
        """
        Switch switchboard to charging mode
        """
        pass

    def switch_to_normal_mode(self, *args, **kwargs):
        """
        Switch switchboard to normal mode
        """
        pass

    @abstractmethod
    def find_switch(self, *args, **kwargs):
        """
        Find switch board
        """
        pass

    @abstractmethod
    def connect(self, port, verbose=True, *args, **kwargs):
        """
        Connect port on switch board

        Args:
            port (int or str): Port identifier on switchboard
            verbose (bool): Propagate message to logger
        """
        pass

    @abstractmethod
    def disconnect(self, verbose, port=None, *args, **kwargs):
        """
        Disconnect all on switch board.
        Port parameter option is not required.

        Args:
            verbose (bool): Propagate message to logger
            port (int or str): Port identifier on switchboard. "None" value mean disconnect all ports.
        """
        pass
