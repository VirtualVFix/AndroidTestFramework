# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "1/8/2018 11:55 AM"
__doc__ = 'Tests of CMD manager class and base functionality of ADB, ADB shell and Fastboot classes'

import unittest
from time import sleep
from config import CONFIG
from libs.cmd.manager import Manager
from libs.cmd.implement import exceptions


class BaseTestCase(unittest.TestCase):
    """
    CMD manager tests
    """
    debug_serial = None  # serial number of device with Userdebug build
    user_serial = None  # serial number of device with User build
    default_timeout = 90  # default timeout for wait device

    @classmethod
    def setUpClass(cls):
        # Debug build manager
        cls.man = Manager(serial=cls.debug_serial or CONFIG.DEVICE.SERIAL)
        # User build manager
        # if cls.user_serial:
        #     cls.user_man = Manager(serial=cls.user_serial or CONFIG.DEVICE.SERIAL)
        # else:
        #     cls.man.logger.warning('Serial number of device with User build not set !')

    @classmethod
    def tearDownClass(cls):
        try:
            cls.man.reboot_to('adb', timeout=cls.default_timeout, verbose=False)
        except: pass

    def setUp(self):
        # check serial
        self.assertNotEqual(self.man.serial, None, 'Serial number is not set !')
        # reboot device each test
        self.man.reboot_to('adb', timeout=self.default_timeout, verbose=False)

    def test01(self):
        """ debug root | get root access on Debug build """
        self.man.reboot_to('adb', timeout=self.default_timeout, force=True)
        self.assertTrue(self.man.root(timeout=self.default_timeout), 'Root cannot be got')

    def test02(self):
        """ debug double root | get root access twice on Debug build """
        self.man.reboot_to('adb', timeout=self.default_timeout, force=True)
        self.assertTrue(self.man.root(timeout=self.default_timeout), 'Root cannot be got')
        sleep(1)
        self.assertTrue(self.man.root(timeout=self.default_timeout), 'Root cannot be got')

    def test03(self):
        """ user root | get root access on User build """
        self.man.reboot_to('adb', timeout=self.default_timeout, force=True)
        # self.assertIsNotNone(self.user_serial, 'Serial number of device with User build not set !')
        # self.assertTrue(self.user_man.root(timeout=self.default_timeout), 'Root cannot be got')
        mn = Manager(serial='emulator')
        mn.logger.warning('Testing with emulator !')
        self.assertFalse(mn.root(__emulator_command_response__='root cannot be got on product build'),
                         'Root was provided on User build !')

    def test04(self):
        """ root timeout | root timeout expired """
        self.man.adb.reboot()
        with self.assertRaises(exceptions.TimeoutExpiredError):
            self.man.root(timeout=1)

    def test10(self):
        """ remount """
        self.man.reboot_to('adb', timeout=self.default_timeout, force=True)
        self.assertIsNone(self.man.remount())

    def test11(self):
        """ remount timeout | remount timeout expired """
        self.man.adb.reboot()
        with self.assertRaises(exceptions.TimeoutExpiredError):
            self.man.remount(timeout=1)

    def test20(self):
        """ wait adb | wait for device in adb """
        self.man.adb.reboot()
        self.assertIsNone(self.man.wait_for('adb', timeout=self.default_timeout))

    def test21(self):
        """ wait adb timeout | wait_for in adb timeout expired """
        self.man.adb.reboot()
        with self.assertRaises(exceptions.TimeoutExpiredError):
            self.man.wait_for('adb', timeout=1)

    def test30(self):
        """ wait fastboot | wait for device in fastboot """
        self.man.adb.reboot_bootloader()
        self.assertIsNone(self.man.wait_for('fastboot', timeout=self.default_timeout))

    def test31(self):
        """ wait fastboot timeout | wait_for in adb timeout expired """
        self.man.adb.reboot_bootloader()
        with self.assertRaises(exceptions.TimeoutExpiredError):
            self.man.wait_for('fastboot', timeout=1)

    def test40(self):
        """ get modes """
        mode = self.man.get_mode(timeout=self.default_timeout)
        self.assertEqual(mode, 'adb', '"%s" mode found instead of "adb"' % mode)
        self.man.reboot_to('fastboot', timeout=self.default_timeout)
        mode = self.man.get_mode(timeout=self.default_timeout)
        self.assertEqual(mode, 'fastboot', '"%s" mode found instead of "fastboot"' % mode)

    def test50(self):
        """ first detect adb | first detect device in ADB. May error if more one device connected """
        if self.user_serial is not None:
            raise unittest.SkipTest('More one device used !')

        mn = Manager(serial=None)
        ser, mode = mn.first_detect(timeout=self.default_timeout)
        self.assertEqual(ser, self.man.serial, 'Serials not equal')
        self.assertEqual(mode, 'adb', 'Detect mode not equal')
        
    def test51(self):
        """ first detect fastboot | first detect device in FASTBOOT. May error if more one device connected """
        if self.user_serial is not None:
            raise unittest.SkipTest('More one device used !')

        self.man.reboot_to('fastboot', timeout=self.default_timeout)
        mn = Manager(serial=None)
        ser, mode = mn.first_detect(timeout=self.default_timeout)
        self.assertEqual(ser, self.man.serial, 'Serials not equal')
        self.assertEqual(mode, 'fastboot', 'Detect mode not equal')

    def test52(self):
        """ first detect adb multi devices | first detect device in ADB with one more phones """
        # use emulator for this test
        mn = Manager(serial=None, adb_type='emulator')
        mn.logger.warning('Testing with emulator !')
        from string import Template
        with self.assertRaises(exceptions.DeviceEnumeratedError):
            mn.first_detect(timeout=self.default_timeout, __emulator_command_response__=
                            Template('List of devices attached\n$SERIAL\tdevice\nXXXXXXXX\tdevice\n'))

    def test53(self):
        """ first detect fastboot multi devices | first detect device in FASTBOOT with one more phones """
        self.man.reboot_to('fastboot', timeout=self.default_timeout)
        mn = Manager(serial=None)
        with self.assertRaises(exceptions.DeviceEnumeratedError):
            mn.first_detect(timeout=self.default_timeout)

    def test54(self):
        """ first detect timeout | first detect device timeout expired """
        self.man.adb.reboot()
        mn = Manager(serial=None)
        with self.assertRaises(exceptions.TimeoutExpiredError):
            mn.first_detect(timeout=1)

    def test60(self):
        """ wait idle | wait for device in idle """
        self.man.adb.reboot()
        self.assertIsNone(self.man.wait_idle(timeout=self.default_timeout))

    def test61(self):
        """ wait idle timeout | wait for device in idle timeout expired """
        self.man.adb.reboot()
        with self.assertRaises(exceptions.TimeoutExpiredError):
            self.man.wait_idle(timeout=1)

    def test70(self):
        """ wait service | wait for service """
        self.man.adb.reboot()
        self.assertIsNone(self.man.wait_service('settings', timeout=self.default_timeout))

    def test71(self):
        """ wait service timeout | wait for service timeout expired """
        with self.assertRaises(exceptions.TimeoutExpiredError):
            self.man.wait_service('wrong_service', timeout=1)

    @staticmethod
    def __generate_file(iterations=10000, name='test.file'):
        """ generate test file for push/pull tests """
        import os
        path = os.path.join(CONFIG.SYSTEM.LOG_PATH, name)
        if not os.path.exists(path):
            with open(path, 'w') as file:
                for x in range(iterations):
                    file.write('LINE %d OF TEST DATA \n' % (x+1))
        return path, name

    @staticmethod
    def __compare_files(path1, path2):
        """ Compare files for push/pull tests """
        import os
        import hashlib
        with open(path1, 'rb') as file:
            md5_f1 = hashlib.md5(file.read()).hexdigest()

        if os.path.exists(path2):
            with open(path2, 'rb') as file:
                md5_f2 = hashlib.md5(file.read()).hexdigest()
        else:
            md5_f2 = path2
        return md5_f1, md5_f2

    def test80(self):
        """ push | push file to device """
        path, name = self.__generate_file()
        self.man.push(path, '/data/local/tmp/', timeout=self.default_timeout, verbose=True)
        md5 = self.man.shell('md5sum /data/local/tmp/%s' % name).strip().split(' ')[0]
        self.assertEqual(*self.__compare_files(path, md5))

    def test81(self):
        """ push timeout | push file to device timeout expired """
        path, name = self.__generate_file(2000000, 'big.file')
        # self.man.adb.reboot()
        # sleep(2)
        with self.assertRaises((exceptions.TimeoutExpiredError, exceptions.DeviceEnumeratedError)):
            self.man.push(path, '/data/local/tmp/', timeout=1, verbose=True)

    def test90(self):
        """ pull | pull file from device """
        path, name = self.__generate_file()
        self.man.push(path, '/data/local/tmp/', timeout=self.default_timeout)
        path1 = path[:-5] + '1.file'
        self.man.pull('/data/local/tmp/%s' % name, path1, timeout=self.default_timeout, verbose=True)
        self.assertEqual(*self.__compare_files(path, path1))

    def test91(self):
        """ pull timeout | pull file from device timeout expired """
        path, name = self.__generate_file(2000000, 'big.file')
        if name not in self.man.sh('ls /data/local/tmp/', empty=False):
            self.man.push(path, '/data/local/tmp/', timeout=300, verbose=True)
        with self.assertRaises((exceptions.TimeoutExpiredError, exceptions.DeviceEnumeratedError)):
            self.man.pull('/data/local/tmp/%s' % name, path[:-5] + '1.file', timeout=1, verbose=True)

    def test100(self):
        """ adb command """
        self.assertTrue('List of devices attached' in self.man.adb('devices'))

    def test101(self):
        """ adb timeout | adb command timeout expired """
        with self.assertRaises(exceptions.TimeoutExpiredError):
            self.man.adb('logcat', timeout=1)

    def test102(self):
        """ adb reboot """
        self.man.adb.reboot()
        sleep(5)
        self.assertFalse(self.man.serial in self.man.adb.devices()[0])

    def test103(self):
        """ adb reboot bootloader """
        self.man.adb.reboot_bootloader()
        mode = self.man.get_mode(timeout=self.default_timeout)
        self.assertEqual('fastboot', mode)

    def test104(self):
        """ adb kill-server """
        self.assertIsNone(self.man.adb.kill_server())

    def test105(self):
        """ adb start-server """
        self.assertIsNone(self.man.adb.start_server())

    def test106(self):
        """ adb version """
        from pkg_resources import parse_version
        self.assertNotEqual(parse_version(''), self.man.adb.version())

    def test107(self):
        """ adb devices """
        ser, dev = self.man.adb.devices()
        self.assertTrue(self.man.serial.upper() in ser)
        self.assertEqual(dev[ser.index(self.man.serial)], 'device')

    def test108(self):
        """ not implement | abstract functions which implemented in Manager """
        with self.assertRaises(NotImplementedError):
            self.man.adb.root()
        with self.assertRaises(NotImplementedError):
            self.man.adb.remount()
        with self.assertRaises(NotImplementedError):
            self.man.adb.pull(None, None)
        with self.assertRaises(NotImplementedError):
            self.man.adb.push(None, None)

    def test110(self):
        """ shell command | adb shell command """
        self.assertTrue('POWERUPREASON' in self.man.shell('cat /proc/bootinfo', verbose=True).upper())

    def test111(self):
        """ shell timeout | adb shell command timeout expired """
        with self.assertRaises(exceptions.TimeoutExpiredError):
            self.man.shell('logcat', timeout=1)

    def test120(self):
        """ fastboot command """
        self.man.reboot_to('fastboot', timeout=self.default_timeout)
        self.assertEquals(self.man.fastboot('oem', 'help', timeout=self.default_timeout), '')

    def test121(self):
        """ fastboot command timeout | fastboot command timeout expired """
        # self.man.reboot_to('fastboot', timeout=self.default_timeout)
        with self.assertRaises(exceptions.TimeoutExpiredError):
            self.man.fastboot('getvar', 'all', timeout=1)

    def test122(self):
        """ fastboot devices """
        self.man.reboot_to('fastboot', timeout=self.default_timeout)
        self.assertTrue(self.man.serial.upper() in self.man.fastboot.devices()[0])

    def test123(self):
        """ fastboot reboot | fastboot reboot to ADB """
        self.man.reboot_to('fastboot', timeout=self.default_timeout)
        self.assertIsNone(self.man.fastboot.reboot())
        self.assertEqual('fastboot', self.man.get_mode(timeout=self.default_timeout))

    def test124(self):
        """ fastboot reboot-bootloader | fastboot reboot to bootloader """
        self.man.reboot_to('fastboot', timeout=self.default_timeout)
        self.assertTrue(self.man.serial.upper() in self.man.fastboot.devices()[0])
        self.assertIsNone(self.man.fastboot.reboot_bootloader())
        self.assertTrue(self.man.serial.upper() in self.man.fastboot.devices()[0])

    def test130(self):
        """ device offline """
        # use emulator for this test
        mn = Manager(serial='emulator')
        mn.logger.warning('Testing with emulator !')
        from string import Template
        with self.assertRaises(exceptions.DeviceEnumeratedError):
            mn.get_mode(timeout=self.default_timeout, __emulator_command_response__ =
            Template('List of devices attached\n$SERIAL\toffline\n'))


    # @SkipByDefault()
    # @NotImplemented
    # def test900(self):
    #     """ root with unauthorized device | not implemented """
    #
    # @SkipByDefault()
    # @NotImplemented
    # def test901(self):
    #     """ root with kill adb-server | not implemented """
    #
    # @SkipByDefault()
    # @NotImplemented
    # def test902(self):
    #     """ remount with disable_verity | not implemented """
    #
    # @SkipByDefault()
    # @NotImplemented
    # def test903(self):
    #     """ remount with disable_wptest | not implemented """
    #
    # @SkipByDefault()
    # @NotImplemented
    # def test904(self):
    #     """ remount with kill adb-server | not implemented """
    #
    # @SkipByDefault()
    # @NotImplemented
    # def test905(self):
    #     """ first detect with unauthorized device | not implemented """
