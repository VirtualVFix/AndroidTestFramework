# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/27/17 14:58"

from .base import Base


class Database(Base):
    """
    Database default config.
    This config is part of :class:`src.libs.core.register.Register`
    """

    def __init__(self):
        super(Database, self).__init__()
