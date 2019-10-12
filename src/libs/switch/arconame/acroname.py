# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/22/18 14:03"

from time import sleep
from config import CONFIG
from ..interface.switch import Switch
from xmlrpc.client import ServerProxy
from libs.switch.base.exceptions import SwitchboardNotFoundError
from libs.core.logger import getLogger, getSysLogger
from .constants import ACRONAME_TAG, DEFAULT_SWITCH_PORT_DISABLE_TIMEOUT


class Acroname(Switch):
    """ Acroname programmable USB hub class """

    def __init__(self, serial, logger=None, **kwargs):
        super(Acroname, self).__init__(serial, logger=None, **kwargs)

        self.serial = serial
        self.logger = logger or getLogger(__file__)
        self.syslogger = getSysLogger()
        self.switchlogger = getLogger(__file__, 'acroname.log', propagate=False)

        # check hub server
        try:
            self.switch = ServerProxy('http://{}:{}'.format(CONFIG.SWITCH.ACRONAME_SERVER_ADDRESS,
                                                            CONFIG.SWITCH.ACRONAME_SERVER_PORT))
        except Exception as e:
            self.syslogger.exception(e)
            raise SwitchboardNotFoundError('Acroname HUB server connection error: %s' % e)

    def is_port_connected(self, port=CONFIG.SWITCH.ACRONAME_PORT):
        """
        Check if port connected

        Args:
            port (int): Port number
        """
        out = self.switch.getHubMode()
        self.switchlogger.info('%s ports status: %s' % (ACRONAME_TAG, out))
        mode = str(bin(out['_value']))[::-1][:-3]
        if len(mode) <= port * 2 or mode[port * 2 + 1] == '0':
            return False
        return True

    def find_switch(self, *args, **kwargs):
        """
        Detect serial numbers of switch and connected device serial

        Returns:
            (str Hub serial number, str full hub serial address) or (None, None)
        """
        if CONFIG.SWITCH.ACRONAME_PORT is not None:
            if not self.is_port_connected():
                self.connect()
                sleep(2)
            return self.serial, 'http://%s:%s' % (CONFIG.SWITCH.ACRONAME_SERVER_ADDRESS,
                                                  CONFIG.SWITCH.ACRONAME_SERVER_PORT)
        return None, None

    def set_disable_port_timeout(self, port=CONFIG.SWITCH.ACRONAME_PORT, timeout=DEFAULT_SWITCH_PORT_DISABLE_TIMEOUT):
        """
        Set timeout in seconds to auto disable port.

        Args:
            port (int): Port identifier on switchboard
            timeout (int): Timeout in seconds to auto disable port
        """
        out = self.switch.setDisableTimeoutForEnabledPort(port, timeout)
        self.switchlogger.info('%s set disable timeout for port [%d] to %d seconds: %s'
                               % (ACRONAME_TAG, port, timeout, out))
        self.switchlogger.info('CONFIG port timeout: %d' % DEFAULT_SWITCH_PORT_DISABLE_TIMEOUT)

    def switch_to_charging_mode(self, port=CONFIG.SWITCH.ACRONAME_PORT, timeout=DEFAULT_SWITCH_PORT_DISABLE_TIMEOUT):
        """
        Switch switchboard to charging mode

        Args:
            port (int): Port identifier on switchboard
            timeout (int): Timeout in seconds to auto disable port
        """

        self.set_disable_port_timeout(port, timeout)
        self.switchlogger.info('%s switch port [%d] to charging mode' % (ACRONAME_TAG, port))
        if not self.is_port_connected(port):
            self.connect(port)

    def switch_to_normal_mode(self, port=CONFIG.SWITCH.ACRONAME_PORT, timeout=None):
        """
        Switch switchboard to normal mode

        Args:
            port (int): Port identifier on switchboard
            timeout (int): Timeout in seconds to auto disable port
        """
        self.switchlogger.info('%s switch port [%d] to normal mode...' % (ACRONAME_TAG, port))
        self.set_disable_port_timeout(port, timeout or 0)

    def connect(self, port=CONFIG.SWITCH.ACRONAME_PORT, verbose=True, *args, **kwargs):
        """
        Connect port on switch board

        Args:
            port (int): Port identifier on switchboard
            verbose (bool): Propagate message to logger
        """
        if verbose:
            self.logger.info('Connecting USB{} port...'.format(port))
        out = self.switch.setPortEnable(port)
        if verbose:
            self.logger.done()
        self.switchlogger.info('%s enable port [%d]: %s' % (ACRONAME_TAG, port, out))

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
        out = self.switch.setPortDisable(port)
        if verbose:
            self.logger.done()
        self.switchlogger.info('%s disable port [%d]: %s' % (ACRONAME_TAG, port, out))
