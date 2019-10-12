# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/27/17 14:58"

from .base import Base


class Unittest(Base):
    """
    Unittest default config. This config is part of :class:`src.libs.core.register.Register`
    """

    #: Keep all available TestCases with TestSuites, but with out Tests.
    #: Variable will be initialized during validating core lib launch options.
    #: Should be dict. Details: :mod:`unittest.scancases`
    AVAILABLE_TEST_CASES = None

    #: All selected TestCases with TestSuites and Tests.
    SELECTED_TEST_CASES = None

    #: Framework self-test mode.
    #: Framework starting to search tests in library folders instead of tests folder
    SELF_TEST = False
    #: Interrupt testing by error
    # INTERRUPT_BY_ERROR = False
    #: Interrupt testing by fail or error
    INTERRUPT_BY_FAIL = False

    #: Keep all used launch options after launch
    USED_OPTIONS = ''

    #: Last error. Updates automatically after error
    __LAST_ERROR__ = None
    #: TestSuite notify. Updates automatically each TestSuite
    __NOTIFICATION__ = ''

    def __init__(self):
        super(Unittest, self).__init__()
