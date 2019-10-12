# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "13/10/17 20:54"

from config import CONFIG
from optparse import OptionGroup
from libs.core.options import Options


class Logs(Options):
    """
    Logs control options.
    """
    def __init__(self):
        super(Logs, self).__init__()

    def group(self, parser):
        group = OptionGroup(parser, 'Logs')
        group.add_option('--logcat-collection', dest='logcat_collection', action="store_true", default=False,
                         help='Enable save logcat from device. All logs saving in log folder. False by default.')
        return group

    @property
    def priority(self):
        return 600

    def validate(self, options):
        CONFIG.SYSTEM.LOG_COLLECTION = options.logcat_collection
