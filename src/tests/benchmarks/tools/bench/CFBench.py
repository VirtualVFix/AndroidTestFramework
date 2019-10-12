# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 13, 2014 12:30:05 AM$"

import ast
from tests.benchmarks.tools.base import App


class CFBench(App):
    """CFBench"""
    def __init__(self, attributes, serial):
        App.__init__(self, attributes, serial)

    def collect_results(self, res_doc):
        res = ast.literal_eval(self.getResults())
        for x in res:
            res_doc.add_name(x[0])
            res_doc.add_result(x[1].replace('%', ''))
