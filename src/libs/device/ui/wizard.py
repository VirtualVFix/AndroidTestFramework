# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "Sep 18, 2017 2:32:42 PM"

from config import CONFIG
from libs.core.logger import getLogger
from .base.uisettings import UISettings
from .base.constants import DEVICE_SETTINGS
from libs.device.ui.base.exceptions import SetupWizardError


class Wizard(UISettings):
    def __init__(self, serial, logger=None):
        super(Wizard, self).__init__(serial, logger=logger or getLogger(__file__))

    def skipSetupWizard(self):
        """
        Skip setupwizard
        """
        self.logger.info('Check for setup wizard...')
        wizard = DEVICE_SETTINGS['SkipSetupWizard']
        if len(CONFIG.TEST.WIFI_POINTS) == 0:
            raise SetupWizardError('WiFi points if not defined in configuration file !')
        wizard['_points'] = [y for x in CONFIG.TEST.WIFI_POINTS for y in x]
        out = self._start(wizard)
        
        if 'skipped' not in out.lower(): 
            raise SetupWizardError('SkipSetupWizard error: {}'.format(out))
        self.logger.info(out.split('.')[0])
        self.logger.done()
