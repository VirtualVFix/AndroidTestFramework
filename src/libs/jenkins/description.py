# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 13, 2017 14:32:00 PM$"

from libs.jenkins.base.constants import DESCRIPTION_MAIN_COLOR
from libs.jenkins.base.constants import DESCRIPTION_BUILD_COLOR, DESCRIPTION_CURRENT_TEST_COLOR


class Description:
    """ Job description formater """
    
    def currectBuildAndDeviceInfo(self, build, device):
        """ current build information: USER_7.1.1_NDX26.82 / MSM8998 NASH (x64) NGNV130006 """
        result = '<b><font color="{}">{}<br>{}</font></b>'.format(DESCRIPTION_BUILD_COLOR,
                                                                  device,
                                                                  build)
        return result
    
    def currectTest(self, text):
        """ current test information """
        result = '<br><br><font color="{}">Current test: </font>'.format(DESCRIPTION_MAIN_COLOR) \
               + '<b><font color="{}">{}</font></b>'.format(DESCRIPTION_CURRENT_TEST_COLOR,
                                                            text)
        return result
    
    def lastDeviceStatus(self, text):
        """ last device status before current test started: 
            battery capacity, battery voltage, temperature if available, suspend success and so on """
        result = ''
        return result
    
    def lastTestsStatus(self, text):
        """ last completed tests status: tests - cycles - PASS/FAIL """
        result = ''
        return result
