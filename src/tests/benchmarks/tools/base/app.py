# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = " $Apr 7, 2014 10:09:27 PM$"

from config import CONFIG
from .constants import APKS_DIR
from libs.device.ui import Wireless
from libs.core.logger import getLogger


class App(Wireless):
    """ Represents application or benchmark """

    def __init__(self, attributes, serial, logger=None):
        super(App, self).__init__(serial=serial, logger=logger or getLogger(attributes["name"]))
        self.attributes = attributes

    def install(self, *args, **kwargs):
        """
        Install benchmark application
        """
        self.installApk(APKS_DIR, self.attributes, allow_x64=True, smart_install=True)
        # install additional application if required
        if 'additional_apk' in self.attributes:
            self.installApk(APKS_DIR, self.attributes['additional_apk'], allow_x64=True, smart_install=True)
        # install AndroidJUnit test application if required
        self.installJUnitTestsLauncher()
    
    def uninstall(self, *args, **kwargs):
        """
        Uninstall benchmark application
        """
        self.uninstallApk(self.attributes)
        # uninstall additional application if required
        if 'additional_apk' in self.attributes:  
            self.uninstallApk(self.attributes['additional_apk'])

    def start(self, dont_touch_my_wifi_bitch = False, *args, **kwargs):
        """ start benchmark """
        # disable wifi
        if not dont_touch_my_wifi_bitch and CONFIG.TEST.__iswifienabled__:
            self.disableWiFiAndPing()
            CONFIG.TEST.__iswifienabled__ = False
        self.launchJUnitTest(self.attributes, clazz=self.attributes['junit'])

    def stop(self, *args, **kwargs):
        self.forceStopJUnitTestsLauncher()

    def collect_results(self, res_doc):
        self.logger.warn('Collect results feature is not implemented !')
