# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 9, 2014 10:12:03 PM$"

from .online import OnlineBenchmark
from libs.core.logger import getLogger


class BrowserBenchmark(OnlineBenchmark):
    def __init__(self, attributes, serial, logger=None):
        super(BrowserBenchmark, self).__init__(attributes, serial, logger=logger or getLogger(__file__))
            
    def install(self, *argc, **argv):
        self.installJUnitTestsLauncher()
        
    def uninstall(self, *argc, **argv):
        pass
