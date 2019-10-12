# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "11/29/2017 3:11 PM"

import unittest
from libs.core.unittest import Tools


class ToolsTestCase(unittest.TestCase):

    def test01(self):
        """ supported_list_int | Check supported variable type of Tools.convert_str_params_to_list """
        # list of int
        var = 'var=[1,2,3]'
        out = Tools.convert_str_params_to_list(var)[0]
        # find variable with value
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0], 'var', 'Variable name not found')
        self.assertListEqual(out[1], [1, 2, 3], 'Result list does not equal')
        self.assertIsInstance(out[1], list, 'Out should be list')
        for i, x in enumerate(out):
            self.assertIsInstance(x, int, 'list[%d] not int' % i)
