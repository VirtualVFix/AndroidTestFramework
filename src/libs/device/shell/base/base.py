# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/21/18 15:43"

from config import CONFIG
from libs.cmd import Manager
from libs.core.logger import getLogger


class Base(Manager):
    """ Base class for device shell utility """

    def __init__(self, serial=None, logger=None):
        super(Base, self).__init__(serial=serial, logger=logger or getLogger(__file__))

    def update_device_info(self):
        """
        Get device info and save to CONFIG.DEVICE
        """
        self.prop.update_cache()
        CONFIG.DEVICE.DEVICE_NAME = self.prop.getDeviceName()
        CONFIG.DEVICE.DEVICE_PRODUCT = self.prop.getProductName()
        CONFIG.DEVICE.BUILD_TYPE = self.prop.getBuildType()
        CONFIG.DEVICE.BUILD_VERSION = self.prop.getBuildVersion()
        CONFIG.DEVICE.BUILD_RELEASE = self.prop.getBuildRelease()
        CONFIG.DEVICE.BUILD_PRODUCT = self.prop.getProductBuild()
        CONFIG.DEVICE.CPU_HW = self.prop.getCPUHW()
        CONFIG.DEVICE.CPU_64_BIT = self.prop.isCPU64Bit()
        CONFIG.DEVICE.BUILD_FINGERPRINT = self.prop.getBuildFingerprint()
