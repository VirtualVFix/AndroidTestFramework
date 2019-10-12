# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Nov 24, 2015 16:56:00 PM$"

import re
from tests.exceptions import ResultsNotFoundError
from tests.benchmarks.tools.base import BrowserBenchmark


class Sunspider(BrowserBenchmark):
    def __init__(self, attributes, serial):
        BrowserBenchmark.__init__(self, attributes, serial)

    def collect_results(self, res_doc):
        raw_res = self.getResults()
        res_values = re.findall('\s([\w\d-]+):\s*([\d.]+)ms', raw_res, re.DOTALL)

        if sum([len(x) for x in res_values]) == 0:
            raise ResultsNotFoundError('Results not found !')
        
        for val in res_values:
            res_doc.add_name(val[0])
            res_doc.add_result(val[1])
