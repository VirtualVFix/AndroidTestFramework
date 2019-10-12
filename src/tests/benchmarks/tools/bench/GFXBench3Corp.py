# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 13, 2014 1:06:22 AM$"

import re
import ast
from tests.benchmarks.tools.base import App
from tests.exceptions import ResultsNotFoundError


class GFXBench3Corp(App):
    """ GLBenchmark 3.x.x & 4.x.x Corporate versions """
    def __init__(self, attributes, serial):
        App.__init__(self, attributes, serial)
        self.expected_results = attributes['results']

    def collect_results(self, res_doc):
        raw = ast.literal_eval(self.getResults())
        empty_score = ['High-Level Tests', 'Low-Level Tests', 'Special Tests']
        
        # check if results not empty
        check = [x[1] for x in raw if len(x) > 1 and x[1] not in [None, '', 'N/A']]
        if len(check) == 0:
            raise ResultsNotFoundError('Results not found !')
        
        res_names = [x[0] for x in raw]
        res_name_index = -1
        for exp_name in self.expected_results:
            res_doc.add_name(exp_name)
            if exp_name in empty_score:
                res_doc.add_result(None)
            elif exp_name in res_names:
                res_name_index = res_names.index(exp_name)
                match = re.search('([\d,.]+)', raw[res_name_index][1], re.DOTALL)
                res_doc.add_result(match.group(1) if match else raw[res_name_index][1])
            elif exp_name == 'fps':                
                if res_name_index != -1 and len(raw[res_name_index]) > 2:
                    match = re.search('([\d,.]+)', raw[res_name_index][2], re.DOTALL)
                    res_doc.add_result(match.group(1) if match else raw[res_name_index][2])
                else: res_doc.add_result('N/A')
            else: 
                res_doc.add_result('N/A')
                res_name_index = -1
