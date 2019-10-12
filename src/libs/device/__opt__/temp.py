# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "13/10/17 20:54"

from config import CONFIG
from optparse import OptionGroup
from libs.core.options import Options
from libs.core.logger import getSysLogger
from libs.core.exceptions import RuntimeInterruptError


class Temp(Options):
    """
    Device temperature control options.
    """

    def __init__(self):
        super(Temp, self).__init__()

    def group(self, parser):
        group = OptionGroup(parser, 'Device temperature control')
        group.add_option('--disable-temperature-control', dest='disable_temperature_control', action="store_true",
                         default=False, help='Disable temperature control.')
        group.add_option('--temperature-level', dest='temperature_level', default=None, help='Temperature threshold.')
        return group

    @property
    def priority(self):
        return 700

    def validate(self, options):
        # temperature control
        CONFIG.DEVICE.ENABLE_TEMPERATURE_CONTROL = not options.disable_temperature_control
        CONFIG.TEST.LOG_COLLECTION = options.logcat_collection
        if options.temperature_level is not None:
            syslogger = getSysLogger()
            try:
                CONFIG.DEVICE.RUN_TEMPERATURE = {'default': int(options.temperature_level)}
                if CONFIG.DEVICE.RUN_TEMPERATURE['default'] > 100 or CONFIG.DEVICE.RUN_TEMPERATURE['default'] < -20:
                    raise RuntimeInterruptError
            except Exception as e:
                syslogger.exception(e)
                raise RuntimeInterruptError('[--temperature-level] option should be integer in -20C-100C range. '
                                            + 'Usage: --temperature-level LEVEL')
