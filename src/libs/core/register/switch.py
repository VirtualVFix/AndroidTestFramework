# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/27/17 14:58"

from .base import Base


class Switch(Base):
    """
    Switch default config. This config is part of :class:`src.libs.core.register.Register`
    """

    #: Switch board class
    CLASS = None
    #: Switch board serial number
    SERIAL = None

    #: Acroname USB hub server address
    ACRONAME_SERVER_ADDRESS = 'localhost'
    #: Acroname USB hub server port
    ACRONAME_SERVER_PORT = None
    #: Acroname USB hub port number
    ACRONAME_PORT = None

    def __init__(self):
        super(Switch, self).__init__()
