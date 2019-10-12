# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "1/8/2018 11:55 AM"
__doc__ = 'Tests of AdbGuard class. Check Adb and Adb shell exception. All tests base on Emulator'

import unittest
from config import CONFIG
from libs.cmd.manager import Manager
from libs.cmd.implement import exceptions


class AdbGuardTestCase(unittest.TestCase):
    """
    AdbGuard of command execution tests
    """

    @classmethod
    def setUpClass(cls):
        # Emulator manager
        cls.man = Manager(serial='emulator')

    def test01(self):
        """ emulator | check emulator works fine """
        self.assertTrue('List of devices attached' in self.man.adb('devices'))

    def test02(self):
        """ access security exception """
        with self.assertRaises(exceptions.AccessDeniedError):
            self.man.adb('security exception', retry_count=0,
                         __emulator_command_response__='java.Exception.SecurityException operation not permitted')

    def test03(self):
        """ access permission error """
        with self.assertRaises(exceptions.AccessDeniedError):
            self.man.adb('permission error', retry_count=0,
                         __emulator_command_response__='\n\nrandomdom... Permission not guaranteed asdasd\n\n\n\n')

    def test04(self):
        """ access permitted error """
        with self.assertRaises(exceptions.AccessDeniedError):
            self.man.adb('permitted error', retry_count=0,
                         __emulator_command_response__='\nOperation is not permitted\n')

    def test05(self):
        """ access error """
        with self.assertRaises(exceptions.AccessDeniedError):
            self.man.adb('access error', retry_count=0,
                         __emulator_command_response__='\nAccess not granted\n')

    def test06(self):
        """ access denied error """
        with self.assertRaises(exceptions.AccessDeniedError):
            self.man.adb('access denied', retry_count=0,
                         __emulator_command_response__='\nAccess denied\n')

    def test07(self):
        """ access root user error """
        with self.assertRaises(exceptions.AccessDeniedError):
            self.man.adb('access denied', retry_count=0,
                         __emulator_command_response__='\nRoot user is requried !\n')

    def test10(self):
        """ command not found """
        with self.assertRaises(exceptions.CommandNotFoundError):
            self.man.adb('command not found', retry_count=0,
                         __emulator_command_response__='\nCommand randomdom: not found.\n')

    def test11(self):
        """ command not recognized """
        with self.assertRaises(exceptions.CommandNotFoundError):
            self.man.adb('command not recognized', retry_count=0,
                         __emulator_command_response__='\nrand: is not recognized as an internal or external command\n')

    def test20(self):
        """ file does not exist """
        with self.assertRaises(exceptions.ObjectDoesNotExistError):
            self.man.adb('file does not exist', retry_count=0,
                         __emulator_command_response__='\n"rand" file does not exist.\n')

    def test21(self):
        """ no such file or directory """
        with self.assertRaises(exceptions.ObjectDoesNotExistError):
            self.man.adb('no such file or directory', retry_count=0,
                         __emulator_command_response__='\n"rand" no such file or directory.\n')

    def test30(self):
        """ syntax error """
        with self.assertRaises(exceptions.CommandSyntaxError):
            self.man.adb('syntax error', retry_count=0,
                         __emulator_command_response__='\n"rand .?as" syntax error.\n')

    def test40(self):
        """ latest fastboot """
        with self.assertRaises(exceptions.ResultError):
            self.man.adb('latest fastboot', retry_count=0,
                         __emulator_command_response__='\nLatest Motorola fastboot is required ! \n')

    def test50(self):
        """ error """
        with self.assertRaises(exceptions.ResultError):
            self.man.adb('error', retry_count=0,
                         __emulator_command_response__='\nError of execution something ! \n')

    def test51(self):
        """ fail """
        with self.assertRaises(exceptions.ResultError):
            self.man.adb('error', retry_count=0,
                         __emulator_command_response__='\nStart process - failed')
