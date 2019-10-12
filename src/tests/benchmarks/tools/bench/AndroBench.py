# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Nov 24, 2015 16:46:00 PM$"

import re
import ast
from tests.benchmarks.tools.base import App


class AndroBench(App):
    def __init__(self, attributes, serial):
        App.__init__(self, attributes, serial)

    def collect_results(self, res_doc):
        res = ast.literal_eval(self.getResults())
        for x in res:
            values = x[1].split(',')
            for value in values: 
                number = re.search('([\d.]+)', value, re.DOTALL|re.I).group(1)
                name = x[0] + ' (' + value.replace(str(number),'').replace('(','').replace(')','').strip() + ')'
                res_doc.add_name(name)
                res_doc.add_result(number)
