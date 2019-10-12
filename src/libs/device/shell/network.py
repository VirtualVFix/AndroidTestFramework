# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Sep 6, 2017 12:00:00 PM$"

from time import time
from .base import Base
from libs.core.logger import getLogger
from libs.device.shell.base.exceptions import LifeNetworkError


class Network(Base):
    """ Operations with device network """
    def __init__(self, serial=None, logger=None):
        super(Network, self).__init__(serial, logger=logger or getLogger(__file__))

    def checkLifeNetwork(self, timeout=30):
        """ check if life mobile network is available """
        self.logger.info('Checking Life Network...')
        states = [x.strip() for x in self.sh('getprop gsm.sim.state', timeout=timeout, remove_line_symbols=True)
            .lower().strip('[]').split(',') if x.strip() != '']
        if 'ready' not in states: 
            raise LifeNetworkError('Life SIM card not detected.')
        else: 
            self.logger.info('Life SIM card is detected.')
            
        t = time()
        while time()-t <= timeout:
            types = [x.strip() for x in self.sh('getprop gsm.network.type', timeout=timeout, remove_line_symbols=True)
                .lower().strip('[]').split(',') if x.strip() != '']
            network = None
            for _type in types: 
                if network is None and _type not in ['unknown', '']:
                    network = _type.upper()
                    self.logger.info('Life network is detected [{}]'.format(network))
                    return                
        raise LifeNetworkError('Life network not found. Timeout expired')
