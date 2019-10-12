# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "10/26/17 17:05"
__doc__ = 'sub test in benchmarks'

import random
import unittest
from config import CONFIG
from libs.core.tools import SkipByDefault, OwnLoop, PassRate


class RegularTestCase(unittest.TestCase):
    dict_var = {'a': 1, 'b': '2', 'c': [1, 3, 4]}
    dict_dict_var = {'a': {'b': 'abc'}}
    list_int_var = [1, 2, 3]
    list_str_var = ['a', 'b', 'c']
    list_float_var = [1.01, 2.02, 3.033]
    str_var = 'abc'
    int_var = 123
    float_var = 1.23
    test06_cycles = 2

    @classmethod
    def setUpClass(cls):
        print('setUpClass origa')

    @classmethod
    def tearDownClass(cls):
        print('tearDownClass origa')

    def setUp(self):
        print('setUp origa')

    def tearDown(self):
        print('tearDown origa')

    @unittest.skip('JUST CAUSE')
    def test01(self):
        """ --first | more description """
        self.assertIsInstance(self.dict_var, dict, 'Not dict')
        self.assertIsInstance(self.dict_var['a'], int, 'Not int in dict')
        self.assertIsInstance(self.dict_var['b'], str, 'Not str in dict')
        self.assertIsInstance(self.dict_var['c'], list, 'Not list in dict')
        self.assertIsInstance(self.dict_var['c'][0], int, 'Not int in list in dict')

        self.assertIsInstance(self.dict_dict_var, dict, 'Not dict')
        self.assertIsInstance(self.dict_dict_var['a'], dict, 'Not dict in dict')
        self.assertIsInstance(self.dict_dict_var['a']['b'], str, 'Not str in dict in dict')

        self.assertIsInstance(self.list_int_var, list, 'Not list')
        for i, x in enumerate(self.list_int_var):
            self.assertIsInstance(x, int, 'Not int in list[%d]' % i)

        self.assertIsInstance(self.list_str_var, list, 'Not list')
        for i, x in enumerate(self.list_str_var):
            self.assertIsInstance(x, str, 'Not str in list[%d]' % i)

        self.assertIsInstance(self.list_float_var, list, 'Not list')
        for i, x in enumerate(self.list_float_var):
            self.assertIsInstance(x, float, 'Not float in list[%d]' % i)

        self.assertIsInstance(self.str_var, str, 'Not str')
        self.assertIsInstance(self.int_var, str, 'Not int')
        self.assertIsInstance(self.float_var, str, 'Not float')

    @OwnLoop()
    @PassRate(95, rate_by_total_cycles=True)
    @SkipByDefault(ifAndroidVersion=8.0, rule="<")
    def test02(self):
        """ second | more description """

        from libs.cmd.manager import Manager
        man = Manager()
        print(man.first_detect(timeout=10))
        # print(man.cmd(('adb',), timeout=2, interactive=False))
        print('Test02 - should fail')
        self.assertEqual(True, False)

    @SkipByDefault(ifPlatform='msm9998', rule='!=')
    @unittest.expectedFailure
    def test03(self):
        """ trees"""
        print('Test03 - expected failure')
        self.assertTrue(False)

    @unittest.expectedFailure
    def test04(self):
        """ trees"""
        print('Test04 - unexpected success')
        self.assertTrue(True)

    @SkipByDefault()
    def test05(self):
        print('Test05 - should pass')
        self.assertEqual(True, True)

    @PassRate(50)
    def test06(self):
        """ second | more description """
        random.seed()
        print('Test06 - should random error')
        if bool(random.randint(0, 1)):
            raise Exception(CONFIG.TEST.CURRENT_CYCLE)
        self.assertTrue(True)
