# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

"""
Todo:
    - check empty --tests without --self-test
    - check empty case delimiter "," in --test
"""

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "10/26/17 17:04"
__doc__ = "Core test"

import unittest


class Test_testTestCase(unittest.TestCase):

    def test01(self):
        self.assertEqual(True, False)
