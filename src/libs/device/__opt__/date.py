# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "13/10/17 20:54"

from config import CONFIG
from optparse import OptionGroup
from libs.core.options import Options


class Date(Options):
    """
    Date and time sync control options.
    """
    def __init__(self):
        super(Date, self).__init__()

    def group(self, parser):
        group = OptionGroup(parser, 'Date and time sync')
        group.add_option('--disable-time-sync', dest='disable_time_sync', action="store_true", default=False,
                         help='Disable date and time sync on device.')
        return group

    @property
    def priority(self):
        return 0

    async def validate(self, options):
        # disable date and time sync
        if options.disable_time_sync is True:
            self.CLEAN_OF_REGISTERED()

    def setup_frame(self):
        """ Sync date on device """
        from libs.device.shell import Date
        Date(CONFIG.DEVICE.SERIAL).syncDate()
