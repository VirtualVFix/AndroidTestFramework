# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 12, 2014 4:40:25 PM$"

import ast
from tests.benchmarks.tools.base import App


class AnTuTu6(App):
    """ AnTuTu 6 """
    def __init__(self, attributes, serial):
        App.__init__(self, attributes, serial)
        
    def collect_results(self, res_doc):
        raw_res = ast.literal_eval(self.getResults())
        for name, value in raw_res:
            res_doc.add_name(name.replace('[','').replace(']',''))
            res_doc.add_result(value)
