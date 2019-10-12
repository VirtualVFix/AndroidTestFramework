# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/22/18 15:13"

from config import CONFIG
from .constants import TAG
from libs.switch.interface.switch import Switch
from libs.core.logger import getLogger, getSysLogger


class FakeBoard(Switch):
    """ Acroname programmable USB hub class """

    def __init__(self, serial, logger=None, **kwargs):
        super(FakeBoard, self).__init__(serial, logger=None, **kwargs)

        self.serial = serial
        self.logger = logger or getLogger(__file__)
        self.syslogger = getSysLogger()
        self.switchlogger = getLogger(__file__, 'fakeboard.log', propagate=False)

    def find_switch(self, *args, **kwargs):
        """
        Detect serial numbers of switch and connected device serial

        Returns:
            (str Hub serial number, str full hub serial address) or (None, None)
        """
        return 'FAKEBOARD'

    def switch_to_normal_mode(self, port=0, timeout=None):
        """
        Switch switchboard to normal mode

        Args:
            port (int): Port identifier on switchboard
            timeout (int): Timeout in seconds to auto disable port
        """
        self.switchlogger.info('%s switch port [%d] to normal mode...' % (TAG, port))

    def connect(self, port=CONFIG.SWITCH.ACRONAME_PORT, verbose=True, *args, **kwargs):
        """
        Connect port on switch board

        Args:
            port (int): Port identifier on switchboard
            verbose (bool): Propagate message to logger
        """
        if verbose:
            self.logger.info('Connecting USB{} port...'.format(port))
        if verbose:
            self.logger.done()
        self.switchlogger.info('%s enable port [%d]: True' % (TAG, port))

    def disconnect(self, port=CONFIG.SWITCH.ACRONAME_PORT, verbose=True, *args, **kwargs):
        """
        Disconnect all on switch board.
        Port parameter option is not required.

        Args:
            verbose (bool): Propagate message to logger
            port (int): Port identifier on switchboard. "None" value mean disconnect all ports.
        """
        if verbose:
            self.logger.info('Disconnecting USB{} port...'.format(port))
        if verbose:
            self.logger.done()
        self.switchlogger.info('%s disable port [%d]: True' % (TAG, port))