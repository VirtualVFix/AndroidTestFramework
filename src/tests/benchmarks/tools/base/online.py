# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 9, 2014 10:07:45 PM$"

from .app import App
from config import CONFIG
from libs.core.logger import getLogger


class OnlineBenchmark(App):
    """some benchmarks that needs internet connection"""
    def __init__(self, attributes, serial, logger=None):
        super(OnlineBenchmark, self).__init__(attributes, serial, logger=logger or getLogger(__file__))

    def start(self, *args, **kwargs):
        if not CONFIG.TEST.__iswifienabled__:
            self.enableWiFiAndPing()
            CONFIG.TEST.__iswifienabled__ = True
        super(OnlineBenchmark, self).start(dont_touch_my_wifi_bitch=True)
