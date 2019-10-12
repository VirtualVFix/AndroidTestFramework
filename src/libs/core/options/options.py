# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "18/10/17 22:16"

from optparse import OptionGroup
from abc import ABCMeta, abstractmethod


class Options(metaclass=ABCMeta):
    """
    Abstract class of Framework launch options.

    Any library may have self launch options and affect Framework behavior on some life stages.

    How to add launch options:
        - Make **__opt__** folder inside libraries directory
        - Make python files inside without **_** in name
        - Create class inheritance from :class:`Options`
        - Override :func:`group` and :func:`validate` functions

    Note:
        Required override :func:`group` and :func:`validate` functions to implement option class.
        All other functions and property are optional.
    """

    def __init__(self):
        self.__registered = []

    @property
    def REGISTERED(self):
        """
        Property list of registered functions. All not empty function will be registered.

        Note:
            Only registered functions may be launched.
        """
        return self.__registered

    @REGISTERED.setter
    def REGISTERED(self, value):
        self.__registered = value

    def CLEAN_OF_REGISTERED(self):
        """ Remove all registered functions except *validate* """
        self.__registered = ['validate'] if 'validate' in self.__registered else []

    @abstractmethod
    def group(self, parser) -> OptionGroup or [OptionGroup]:
        """
        Generate launch option group or group list.

        Args:
            parser (optparse.OptionParser): Main parser to add current group

        Returns:
             optparse.OptionGroup or [optparse.OptionGroup, ...]: Options group
        """
        group = OptionGroup(parser, 'Example group')
        group.add_option('--example', dest='example', action="store_true", default=False, help='Example test option.')
        return group

    @abstractmethod
    async def validate(self, options):
        """
        Asynchronous options validate function.
        Function will be executed after all options will combined and before framework fully initialized.

        Current function may interrupt Framework launch via raise :class:`RuntimeInterruptError` error.
        Message in error will be printed if not empty.

        Args:
           options (OptionParser): Options with all included groups
        """
        pass

    @property
    def priority(self):
        """
        Option group priority in package. Should returns int number (0 by default).

        Returns:
             int: Priority number
        """
        return 0

    def setup_frame(self):
        """
        Function will be executed after Framework fully initialized.

        Current function may interrupt Framework launch via raise :class:`RuntimeInterruptError` error.
        Message in error will be printed if not empty.
        """
        pass

    def teardown_frame(self):
        """
        Functions will be executed after all test completed.
        """
        pass

    def setup_suite(self):
        """
        Functions will be executed before any test from new suite started. Integrated to `setUpClass()` function in
        unittest.TestCase class.
        """
        pass

    def teardown_suite(self):
        """
        Functions will be executed after suite completed. Integrated to `tearDownClass()` function in unittest.TestCase
        class.
        """
        pass

    def setup(self):
        """
        Functions will be executed before each test in unittest suite. Integrated to `setUp()` function in
        unittest.TestCase class.
        """
        pass

    def teardown(self):
        """
        Functions will be executed after each test in unittest suite. Integrated to `tearDown()` function in
        unittest.TestCase class.
        """
        pass
