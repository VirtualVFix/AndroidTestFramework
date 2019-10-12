# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "1/8/2018 11:55 AM"
__doc__ = 'Tests of BaseGuard class. Check base exception and command retries ' \
          'after error include emulation of Switch Board retry. All tests base on Emulator'

import unittest
from config import CONFIG
from libs.cmd.manager import Manager
from libs.cmd.implement import exceptions


class BaseGuardTestCase(unittest.TestCase):
    """
    BaseGuard of command execution tests
    """

    @classmethod
    def setUpClass(cls):
        # Emulator manager
        cls.man = Manager(serial='emulator')

    def test01(self):
        """ emulator | check emulator works fine """
        self.assertTrue('List of devices attached' in self.man.adb('devices'))

    def test02(self):
        """ protocol fault """
        with self.assertRaises(exceptions.AdbInternalError):
            self.man.adb('protocol fault', retry_count=0, __emulator_command_response__='Error: Protocol fault')

    def test03(self):
        """ device not found """
        with self.assertRaises(exceptions.DeviceEnumeratedError):
            self.man.adb('device not found', retry_count=0, __emulator_command_response__='Error: Device not found')

    def test04(self):
        """ device offline """
        with self.assertRaises(exceptions.DeviceEnumeratedError):
            self.man.adb('device offline', retry_count=0, __emulator_command_response__='Error: Device offline')

    def test05(self):
        """ more one device """
        with self.assertRaises(exceptions.MoreOneDeviceError):
            self.man.adb('more one device', retry_count=0,
                         __emulator_command_response__='Error: More than one device detected')

    def test06(self):
        """ android exception """
        with self.assertRaises(exceptions.AdbInternalError):
            self.man.adb('android exception', retry_count=0,
                         __emulator_command_response__='AndroidException: jave.Exception("TEST")')

    @staticmethod
    def __retry(**kwargs):
        """ Retry command response.
            Command returns "success" when retry_count==__test_retry_counters_to_success__,
            otherwise return __test_retry_fail_response__ or raise __test_retry_fail_response__ when
            it is subclass of Exception """
        __test_retry_counters_to_success__ = kwargs.get('__test_retry_counters_to_success__', -1)
        __test_retry_fail_response__ = kwargs.get('__test_retry_fail_response__', 'failed')
        retry_count = kwargs.get('retry_count', 0)
        CONFIG.TEST.__COMMAND_RETRY__ = retry_count
        if retry_count == __test_retry_counters_to_success__:
            return 'success'
        else:
            if isinstance(__test_retry_fail_response__, Exception.__class__):
                raise __test_retry_fail_response__('Test')
            return __test_retry_fail_response__

    def test10(self):
        """ command retry | check if command retry works fine """
        retry_to_success = 2
        CONFIG.TEST.__COMMAND_RETRY__ = 0
        self.assertEqual(self.man.adb('timeout retry',
                                      retry_delay=0,
                                      switch_reconnect_after=0,
                                      retry_count=retry_to_success+2,
                                      __test_retry_counters_to_success__=retry_to_success,
                                      __emulator_command_response__=self.__retry,
                                      __test_retry_fail_response__="Error: Protocol fault"),
                         'success', 'Command retry does not work !')
        # check retry counter was set
        self.assertEqual(CONFIG.TEST.__COMMAND_RETRY__, retry_to_success, 'Retry counter was not set to config !')

    def test11(self):
        """ timeout retry | check if command retry after timeout works fine """
        retry_to_success = 2
        CONFIG.TEST.__COMMAND_RETRY__ = 0
        self.assertEqual(self.man.adb('command retry',
                                      retry_delay=0,
                                      switch_reconnect_after=0,
                                      allow_timeout_retry=True,
                                      retry_count=retry_to_success+2,
                                      __test_retry_counters_to_success__=retry_to_success,
                                      __emulator_command_response__=self.__retry,
                                      __test_retry_fail_response__=exceptions.TimeoutExpiredError),
                         'success', 'Timeout retry doesn not work !')
        # check retry counter was set
        self.assertEqual(CONFIG.TEST.__COMMAND_RETRY__, retry_to_success, 'Retry counter was not set to config !')

    def test12(self):
        """ retry raise | raise exception if retry doesn't help """
        CONFIG.TEST.__COMMAND_RETRY__ = -1
        with self.assertRaises(exceptions.AdbInternalError):
            self.man.adb('retry raise',
                         retry_count=3,
                         retry_delay=0,
                         switch_reconnect_after=0,
                         __test_retry_counters_to_success__=-1,
                         __emulator_command_response__=self.__retry,
                         __test_retry_fail_response__="Error: Protocol fault")
        # check retry counter was set
        self.assertEqual(CONFIG.TEST.__COMMAND_RETRY__, 0, 'Retry counter was not set to config !')

    def test13(self):
        """ retry disable | check if command retry can be disabled """
        CONFIG.TEST.__COMMAND_RETRY__ = 0
        with self.assertRaises(exceptions.AdbInternalError):
            self.man.adb('timeout retry',
                         retry_delay=0,
                         switch_reconnect_after=0,
                         retry_count=0,
                         __test_retry_counters_to_success__=1,
                         __emulator_command_response__=self.__retry,
                         __test_retry_fail_response__="Error: Protocol fault")
        # check retry counter was set
        self.assertEqual(CONFIG.TEST.__COMMAND_RETRY__, 0, 'Retry counter was not set to config !')

    # Fake Switch board class
    class FakeSwitch:
        def __init__(self, *args, **kwargs):
            if not hasattr(CONFIG.SWITCH, '__TEST_CONNECTED__') or CONFIG.SWITCH.__TEST_CONNECTED__ < 0:
                CONFIG.SWITCH.__TEST_CONNECTED__ = 0
            if not hasattr(CONFIG.SWITCH, '__TEST_DISCONNECTED__') or CONFIG.SWITCH.__TEST_DISCONNECTED__ < 0:
                CONFIG.SWITCH.__TEST_DISCONNECTED__ = 0

        def connect(self):
            CONFIG.SWITCH.__TEST_CONNECTED__ += 1

        def disconnect(self):
            CONFIG.SWITCH.__TEST_DISCONNECTED__ += 1

    def test20(self):
        """ switch success | switch reconnect works fine """

        # save current switch class
        current_switch_board = CONFIG.SWITCH.CLASS
        CONFIG.SWITCH.CLASS = self.FakeSwitch
        CONFIG.SWITCH.__TEST_CONNECTED__ = -1
        CONFIG.SWITCH.__TEST_DISCONNECTED__ = -1

        retry_to_success = 2
        CONFIG.TEST.__COMMAND_RETRY__ = 0
        try:
            self.assertEqual(self.man.adb('switch reconnect success',
                             retry_count=retry_to_success+2,
                             retry_delay=0,
                             switch_reconnect_after=retry_to_success,
                             switch_reconnect_delay=0,
                             __test_retry_counters_to_success__=retry_to_success,
                             __emulator_command_response__=self.__retry,
                             __test_retry_fail_response__="Error: Device not found"),
                             'success', 'Command retry does not work !')
            # check retry counter was set
            self.assertEqual(CONFIG.TEST.__COMMAND_RETRY__, retry_to_success, 'Retry counter was not set to config !')
            # check switch board was reconnected
            self.assertEqual(CONFIG.SWITCH.__TEST_CONNECTED__, 1, 'Switch port connect counter not equal !')
            self.assertEqual(CONFIG.SWITCH.__TEST_DISCONNECTED__, 1, 'Switch port disconnect counter not equal !')
        except:
            raise
        finally:
            CONFIG.SWITCH.CLASS = current_switch_board

    def test21(self):
        """ switch raise | raise after command retry and switch reconnect doesn't help """

        # save current switch class
        current_switch_board = CONFIG.SWITCH.CLASS
        CONFIG.SWITCH.CLASS = self.FakeSwitch
        CONFIG.SWITCH.__TEST_CONNECTED__ = -1
        CONFIG.SWITCH.__TEST_DISCONNECTED__ = -1

        CONFIG.TEST.__COMMAND_RETRY__ = 0
        try:
            with self.assertRaises(exceptions.DeviceEnumeratedError):
                self.man.adb('switch reconnect raise',
                             retry_count=3,
                             retry_delay=0,
                             switch_reconnect_after=1,
                             switch_reconnect_delay=0,
                             __test_retry_counters_to_success__=-1,
                             __emulator_command_response__=self.__retry,
                             __test_retry_fail_response__="Error: Device not found")
            # check retry counter was set
            self.assertEqual(CONFIG.TEST.__COMMAND_RETRY__, 0, 'Retry counter was not set to config !')
            # check switch board was reconnected
            self.assertEqual(CONFIG.SWITCH.__TEST_CONNECTED__, 3, 'Switch port connect counter not equal !')
            self.assertEqual(CONFIG.SWITCH.__TEST_DISCONNECTED__, 3, 'Switch port disconnect counter not equal !')
        except:
            raise
        finally:
            CONFIG.SWITCH.CLASS = current_switch_board

    def test22(self):
        """ switch disable | switch reconnection can be disabled """

        # save current switch class
        current_switch_board = CONFIG.SWITCH.CLASS
        CONFIG.SWITCH.CLASS = self.FakeSwitch
        CONFIG.SWITCH.__TEST_CONNECTED__ = -1
        CONFIG.SWITCH.__TEST_DISCONNECTED__ = -1

        retry_to_success = 2
        CONFIG.TEST.__COMMAND_RETRY__ = 0
        try:
            self.assertEqual(self.man.adb('switch reconnect disable',
                                          retry_count=retry_to_success + 2,
                                          retry_delay=0,
                                          switch_reconnect_after=0,
                                          switch_reconnect_delay=0,
                                          __test_retry_counters_to_success__=retry_to_success,
                                          __emulator_command_response__=self.__retry,
                                          __test_retry_fail_response__="Error: Device not found"),
                             'success', 'Command retry does not work !')
            # check retry counter was set
            self.assertEqual(CONFIG.TEST.__COMMAND_RETRY__, retry_to_success, 'Retry counter was not set to config !')
            # check switch board was reconnected
            self.assertEqual(CONFIG.SWITCH.__TEST_CONNECTED__, -1, 'Switch port connect counter not equal !')
            self.assertEqual(CONFIG.SWITCH.__TEST_DISCONNECTED__, -1, 'Switch port disconnect counter not equal !')
        except:
            raise
        finally:
            CONFIG.SWITCH.CLASS = current_switch_board
