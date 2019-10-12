# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "13/10/17 20:54"

from config import CONFIG
from optparse import OptionGroup
from libs.core.options import Options
from libs.core.logger import getLoggers
from libs.device.shell.base import Base
from libs.core.exceptions import RuntimeInterruptError
from libs.cmd.implement.exceptions import DeviceEnumeratedError
from libs.cmd.implement.constants import DEFAULT_FIRST_DEVICE_DETECT_TIMEOUT


class Hardware(Options):
    """
    Device serial number parameters.
    Detect device and update device info in **CONFIG.DEVICE**
    """

    def __init__(self):
        super(Hardware, self).__init__()

    def group(self, parser):
        group = OptionGroup(parser, 'Device identification')
        group.add_option('-s', '--serial', dest='serial', default=None, help='Device serial number.')
        return group

    @property
    def priority(self):
        return 999

    async def validate(self, options):
        logger, syslogger = getLoggers(__file__)
        man = Base(serial=options.serial)
        try:
            # Try to detect one device when serial not set
            if options.serial is None:
                serial, mode = await man.first_detect(timeout=DEFAULT_FIRST_DEVICE_DETECT_TIMEOUT, verbose=False)
                man.serial = serial
            else:
                # wait for device mode
                mode = await man.async_get_mode(timeout=DEFAULT_FIRST_DEVICE_DETECT_TIMEOUT)
                serial = options.serial

            # device not found
            if serial is None:
                raise DeviceEnumeratedError('Device not found !')

            # device found
            CONFIG.DEVICE.SERIAL = serial
            man.update_device_info()
            logger.newline(syslogger)
            logger.info('Found device [%s] in %s mode !' % (serial, mode.upper()), syslogger)
            logger.info('Device Info: %s [%s (%s)][%s_%s_%s]'
                        % (CONFIG.DEVICE.CPU_HW.upper() or 'undefined',
                           CONFIG.DEVICE.DEVICE_NAME.upper(), 'x64' if CONFIG.DEVICE.CPU_64_BIT else 'x32',
                           CONFIG.DEVICE.BUILD_RELEASE.upper() or 'undefined',
                           CONFIG.DEVICE.BUILD_TYPE.upper() or 'undefined',
                           CONFIG.DEVICE.BUILD_VERSION or 'undefined'), syslogger)
            logger.info('Build fingeprint: %s' % man.prop.getBuildFingerprint(), syslogger)
            logger.newline(syslogger)
        except Exception as e:
            syslogger.exception(e)
            raise RuntimeInterruptError('Device not found !')
