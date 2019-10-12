# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/27/17 14:58"

from .base import Base


class Jenkins(Base):
    """
    Test default config. This config is part of :class:`src.libs.core.register.Register`
    """

    INTEGRATE = False  #: Use Jenkins intergation

    def __init__(self):
        super(Jenkins, self).__init__()
