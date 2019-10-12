# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "Sep 18, 2017 12:16:32 PM"

import re
from time import time
from config import CONFIG
from libs.core.logger import getLogger
from pkg_resources import parse_version
from .base.uisettings import UISettings
from .base.constants import DEVICE_SETTINGS
from libs.device.ui.base.exceptions import WirelessSetingsError, TrafficError


class Wireless(UISettings):
    def __init__(self, serial, logger=None):
        super(Wireless, self).__init__(serial, logger=logger or getLogger(__file__))
        
    def switchAirplaneMode(self, enable):
        """ 
        Switch Airplane mode via shell 
        
        Args:
            enable (bool): Enable or disable airplane mode
        """
        self.logger.info('%s airplane mode...' % 'Enabling' if enable else 'Disabling')
        
        def command():
            self.sh('settings put global airplane_mode_on %d' % enable, errors=True, empty=True)
            out = self.sh('settings get global airplane_mode_on', errors=True, empty=False, remove_line_symbols=True)
            if int(out) != enable:
                raise WirelessSetingsError('Airplane mode cannot be %s !' % 'enabled' if enable else 'disabled')
        
        if self._serviceCommand(command):
            if parse_version(CONFIG.DEVICE.BUILD_RELEASE) < parse_version('8.0'):
                self.sh('am broadcast -a android.intent.action.AIRPLANE_MODE --ez state %s' % str(enable).lower(),
                        errors=True, empty=False)
        else:
            self.logger.error('Airplane mode cannot be %s !' % 'enabled' if enable else 'disabled')
        self.logger.done()
        
    def enableAirplaneMode(self):
        """ Enable Airplane mode """
        self.switchAirplaneMode(enable=True)
        
    def disableAirplaneMode(self):
        """ Disable Airplane mode """
        self.switchAirplaneMode(enable=False)    
        
    def connectToWiFiPoint(self):
        self.logger.info('Connecting to WiFi point...')
        wifi = DEVICE_SETTINGS['WiFiConnectToPoint']
        if len(CONFIG.TEST.WIFI_POINTS) == 0:
            raise WirelessSetingsError('WiFi points if not defined in configuration file !')

        wifi['_points'] = [y for x in CONFIG.TEST.WIFI_POINTS for y in x]
        out = self._start(wifi)
        out = [x.strip() for x in out.split(':') if x.strip() != '']
        if len(out) < 2: 
            raise WirelessSetingsError('WiFi cannot be connected to point !')

        self.logger.info('WiFi status "{}" for "{}" point.'.format(out[0], out[1]))
        self.logger.done()
    
    def isWiFiEnabled(self):
        wifi = DEVICE_SETTINGS['WiFiStatus']
        out = self._start(wifi)
        if 'true' in out.lower(): 
            return True
        return False
    
    def enableWiFi(self):
        """ turn WiFi on """
        wifi = DEVICE_SETTINGS['WiFiEnable']
        self._start(wifi)
    
    def disableWiFi(self):
        """ turn WiFi off """
        wifi = DEVICE_SETTINGS['WiFiDisable']
        self._start(wifi)
        
    def enableWiFiAndPing(self):
        """ connect to WiFi point and ping web sites from config file """
        self.connectToWiFiPoint()
        self.waitForInternerConnection()
    
    def disableWiFiAndPing(self):
        """ disable WiFi and ping web sites from config file """
        self.logger.info('Disable WiFi...')
        self.disableWiFi()
        try:
            self.waitForInternerConnection(timeout=2)
            raise WirelessSetingsError('Wifi is not turned off or Airplane mode is not enabled.')
        except TrafficError:
            pass
        self.logger.done()
    
    def waitForInternerConnection(self, address = CONFIG.TEST.PING_ADDRESS_LIST, timeout = CONFIG.TEST.PING_TIMEOUT):
        """ Ping web sites from config """
        self.logger.info('Check for internet connection...')
        res = ''
        for x in address:
            t = time()
            while (time() - t) < timeout:
                res = self.sh('ping -w 2 ' + x)
                if 'unknown host' in res.lower(): 
                    break
                match = re.search('\s0% packet loss', res, re.I)
                if match: 
                    self.logger.info('connection: ok')
                    return
        self.logger.info('no connection')
        raise TrafficError('Ping ({}) error: {}'.format(address, res))
