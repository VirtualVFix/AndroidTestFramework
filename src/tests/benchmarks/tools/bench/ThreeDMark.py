# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 26, 2014 1:15:13 PM$"

import re
import ast
from tests.benchmarks.tools.base import App


class ThreeDMark(App):
    """ 3DMark bench """
    def __init__(self, attributes, serial):
        App.__init__(self, attributes, serial)

    def install(self, *args, **kwargs):
        # remove content if available
        try:
            self.sh('rm -r {}'.format(self.attributes['push'][1], timeout = 300))
        except:
            pass
        super(ThreeDMark, self).install(*args, **kwargs)

    def collect_results(self, res_doc):
        res = ast.literal_eval(self.getResults())
        for x in res:
            res_doc.add_name(x[0].strip())
            match = re.search('[\d.]+', x[1], re.DOTALL)
            res_doc.add_result(match.group() if match else x[1])
