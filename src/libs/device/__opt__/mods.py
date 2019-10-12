# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "13/10/17 20:54"

from config import CONFIG
from optparse import OptionGroup
from libs.core.options import Options


class Mods(Options):
    """
    Mods control options.
    """
    def __init__(self):
        super(Mods, self).__init__()

    def group(self, parser):
        group = OptionGroup(parser, 'Mods')
        group.add_option('--enable-mods', dest='enable_mods', action="store_true", default=False,
                         help='Enable Mods if available. Mods will be ON before and OFF after testing.')
        return group

    @property
    def priority(self):
        return 500

    def validate(self, options):
        # enable mods
        if options.enable_mods:
            CONFIG.SYSTEM.MODS_ENABLE = True
