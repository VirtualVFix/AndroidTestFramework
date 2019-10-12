# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "12/5/2017 10:32 AM"

from libs.core.options import Options
from libs.core.database import DataBase
from optparse import OptionGroup, SUPPRESS_HELP


class DB(Options):
    """ DataBase options """

    def __init__(self):
        super(DB, self).__init__()

    def group(self, parser):
        group = OptionGroup(parser, '')
        group.add_option('--skip-db', dest='skip_db', action="store_true", default=False, help=SUPPRESS_HELP)
        return group

    async def validate(self, options):
        if options.skip_db is False:
            # wait DB connection
            await DataBase.connect()
