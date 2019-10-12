# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "13/10/17 20:54"

from config import CONFIG
from optparse import OptionGroup
from libs.core.options import Options
from libs.core.logger import getLoggers
from libs.core.exceptions import RuntimeInterruptError


class Battery(Options):
    """
    Device battery control options.
    """
    def __init__(self):
        super(Battery, self).__init__()

    def group(self, parser):
        group = OptionGroup(parser, 'Device battery control')
        group.add_option('--disable-battery-control', dest='disable_battery_control', action="store_true",
                         default=False, help='Disable battery control.')
        group.add_option('--battery-levels', dest='battery_levels', default=None,
                         help='Min/max battery level. Using: --battery-levels "MIN,MAX". '
                              + 'Script will charging phone to maximal level if device discharging to minimal '
                              + 'level threshold.'
                              + 'BATTERY_CONTROL_LEVELS setting from CONFIG will be used if battery levels '
                              + 'not set via option.')
        return group

    @property
    def priority(self):
        return 800

    def validate(self, options):
        logger, syslogger = getLoggers(__file__)

        # device control
        CONFIG.DEVICE.BATTERY_CONTROL = not options.disable_battery_control
        if options.battery_levels is not None:
            try:
                CONFIG.DEVICE.BATTERY_CONTROL_LEVELS = \
                    [int(x) for x in options.battery_levels.split(',') if x.strip() != ''][:2]
                if CONFIG.DEVICE.BATTERY_CONTROL_LEVELS[0] >= CONFIG.DEVICE.BATTERY_CONTROL_LEVELS[1] or \
                        CONFIG.DEVICE.BATTERY_CONTROL_LEVELS[0] < 1 or CONFIG.DEVICE.BATTERY_CONTROL_LEVELS[1] > 99:
                    raise RuntimeInterruptError
            except Exception as e:
                syslogger.exception(e)
                raise RuntimeInterruptError('In [--battery-levels] option should be only integer number in 1-99 range.'
                                            ' Usage: --battery-levels "MIN,MAX"')

        # enable battery control warning
        if CONFIG.DEVICE.BATTERY_CONTROL:
            logger.newline(syslogger)
            logger.warning('Battery control is enabled ! Battery level thresholds are [%d%%-%d%%] '
                           % (CONFIG.DEVICE.BATTERY_CONTROL_LEVELS[0], CONFIG.DEVICE.BATTERY_CONTROL_LEVELS[1])
                           + '(Use [--battery-levels] option to change levels '
                           + 'or [--disable-battery-control] to control disable)', syslogger)
            logger.newline(syslogger)
