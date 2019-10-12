# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Nov 24, 2015 16:56:00 PM$"

import re
from tests.benchmarks.tools.base import BrowserBenchmark


class Octane(BrowserBenchmark):
    def __init__(self, attributes, serial):
        BrowserBenchmark.__init__(self, attributes, serial)

    def collect_results(self, res_doc): 
        raw_res = self.getResults()
        raw_res = raw_res[raw_res.find('2.0 Octane')+10:]
        res_values = re.findall('([\w.]+)[\s\n:]*([\d]+)\s', raw_res, re.DOTALL|re.I)
        if not 'Score' in raw_res:
            score = 1
            for x in res_values: score *= int(x[1])
            score = int(round(score**(1.0/len(res_values))))
            res_doc.add_name("Score")
            res_doc.add_result(score)
        for name, value in res_values:
            res_doc.add_name(name)
            res_doc.add_result(value)
