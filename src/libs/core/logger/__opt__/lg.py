# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/21/18 14:34"

from optparse import OptionGroup
from libs.core.options import Options
from libs.core.logger.logger import tearDownLogger


class Lg(Options):
    """
    Logger group
    """

    def __init__(self):
        super(Lg, self).__init__()
        self.__logs_cleanup = True

    def group(self, parser):
        group = OptionGroup(parser, 'Logger parameters')
        group.add_option('--disable-logs-cleanup', dest='disable_logs_cleanup', action="store_true", default=False,
                         help='Stop cleanup excess logs in log folder. Default False')
        return group

    def validate(self, options):
        # keep value
        self.__logs_cleanup = not options.disable_logs_cleanup

    def teardown_frame(self):
        """ Remove logs files when Framework close """
        # clear some logs
        if self.__logs_cleanup:
            tearDownLogger()
