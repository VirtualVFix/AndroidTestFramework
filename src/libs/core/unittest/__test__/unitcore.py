# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/26/18 12:28"

import random
import unittest
from config import CONFIG
from libs.core.tools import OwnLoop


class UnitCoreTestCase(unittest.TestCase):
    test01_cycles = 10
    test03_cycles = 3

    def setUp(self):
        if self.id().endswith('test03'):
            raise Exception('Error in setUp')

    # @classmethod
    # def setUpClass(cls):
    #     raise Exception('Error in setUpClass')

    # @classmethod
    # def tearDownClass(cls):
    #     raise Exception('Error in tearDownClass')

    def test01(self):
        """ random error | Error in random cycle of test auto-loop """
        rnd = random.randint(0, 10000)
        if rnd % 2 == 0:
            raise Exception('Test exception on %d' % rnd)

    def test02(self):
        """ pass """
        self.assertTrue(True)

    def test03(self):
        """ setup error | error in setup"""
        self.assertTrue(True)

    def test04(self):
        """ pass after setup error """
        self.assertTrue(True)

    @OwnLoop()
    def test05(self):
        """ ownloop """
        CONFIG.TEST.TOTAL_CYCLES = 10
        for i in range(10):
            self.assertTrue(True)
            CONFIG.TEST.CURRENT_CYCLE = i+1
