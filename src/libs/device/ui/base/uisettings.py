# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Jan 26, 2017 2:58:16 PM$"

from .junitrunner import JUnitRunner
from libs.core.logger import getLogger


class UISettings(JUnitRunner):
    """ Represents application or benchmark """
    def __init__(self, serial, logger=None):
        super(UISettings, self).__init__(serial, logger=logger or getLogger(__file__))
        
    def _start(self, arguments):
        self.wait_idle()
        self.installJUnitTestsLauncher()
        self.launchJUnitTest(arguments, clazz=arguments['junit'], function=arguments['function'])
        return self.getResults()
    
    def _serviceCommand(self, function, *args, **kwards):
        """ 
        Retring function with wait for service "settings" if function failed.
        
        Args:
            function (func): Function to execute service command and check result

        Returns:
            True if no error and False otherwise
        """
        
        try:
            function(*args, **kwards)
        except Exception as e:
            self.syslogger.exception(e)
            try:
                self.wait_service('settings')
                function(*args, **kwards)
            except Exception as e:
                self.syslogger.exception(e)
                return False
        return True
