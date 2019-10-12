# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "13/10/17 20:54"


from config import CONFIG
from optparse import OptionGroup
from libs.core.options import Options
from libs.core.logger import getLoggers
from libs.core.exceptions import RuntimeInterruptError
from libs.switch.base.exceptions import SwitchboardNotFoundError, SwitchboardError
from libs.switch.arconame.constants import DEFAULT_SWITCH_PORT_DISABLE_TIMEOUT


class Acroname(Options):
    """
    Detect Acroname USB hub and save Acroname class to **CONFIG.SWITCH.CLASS**
    and hub serial number to **CONFIG.SWITCH.SERIAL**
    """

    def __init__(self):
        super(Acroname, self).__init__()

    def group(self, parser):
        group = OptionGroup(parser, 'Acroname programmable USB hub')
        group.add_option('--server-address', dest='server_address', default='localhost',
                         help='Acroname hub server address. "localhost" by default.')
        group.add_option('--server-port', dest='server_port', default=None,
                         help='Acroname hub server port.')
        group.add_option('--hub-port', dest='hub_port', default=None,
                         help='Port number on Acroname hub.')
        return group

    @property
    def priority(self):
        return 999

    def setup_frame(self):
        """
        Disable auto disable port by timeout
        """
        self.switch.set_disable_port_timeout(timeout=0)
        if not self.switch.is_port_connected():
            self.switch.connect()

    def teardown_frame(self):
        """
        Return auto disable port timeout to default value
        """
        self.switch.set_disable_port_timeout(timeout=DEFAULT_SWITCH_PORT_DISABLE_TIMEOUT)
        self.switch.disconnect()

    async def validate(self, options):
        logger, syslogger = getLoggers(__file__)

        if options.server_port:
            # cannot be used with other hubs
            if options.warthog_serial is not None or options.warthog_find_via_device:
                raise SwitchboardError('Aconame USB hub cannot be used with Warthog switchboards at same time !')

            if options.hub_port is None:
                raise SwitchboardError('Acroname USB hub port number is not defined. '
                                            + 'Please specify [--hub-port] option.')

            try:
                # setup config
                CONFIG.SWITCH.ACRONAME_SERVER_ADDRESS = options.server_address
                CONFIG.SWITCH.ACRONAME_SERVER_PORT = int(options.server_port)
                CONFIG.SWITCH.ACRONAME_PORT = int(options.hub_port)

                url = 'http://%s:%s' % (CONFIG.SWITCH.ACRONAME_SERVER_ADDRESS, CONFIG.SWITCH.ACRONAME_SERVER_PORT)

                # looking for switchboard
                from libs.switch import Acroname

                hub = Acroname(None)
                serial = hub.find_switch()[1]
                if serial is None:
                    raise SwitchboardNotFoundError('Acroname USB hub [%s] not found !' % url)

                CONFIG.SWITCH.CLASS = Acroname
                CONFIG.SWITCH.SERIAL = serial

                # keep hub class
                self.switch = hub

                logger.info('Found Acroname [%s] USB hub by [%s] address !' % (serial, url))
            except Exception as e:
                syslogger.exception(e)
                raise RuntimeInterruptError('Acroname USB hub error: %s' % e)
        else:
            # remove registered functions
            self.CLEAN_OF_REGISTERED()
