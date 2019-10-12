# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 12, 2014 1:46:29 AM$"

import re
from tests.benchmarks.tools.base import App


class Quadrant(App):
    def __init__(self, attributes, serial):
        App.__init__(self, attributes, serial)
        self._result = attributes["result"]
        self.__previuos_results = []
        
    def __get_logcat_results(self, split=False):
        # logcat -d -v raw -b main Timing:I *:S | grep benchmark
        result = self.sh('logcat -d -v time -b main Timing:I *:S | grep benchmark')
        if split is True:
            return result.split('\n')
        return result
    
    def start(self, *args, **kwargs):
        try:
            self.sh('logcat -c')
        except Exception as e:
            self.syslogger.exception(e)
            
        self.__previuos_results = self.__get_logcat_results(split=True)
        super(Quadrant, self).start()

    def collect_results(self, res_doc):
        "This function extracts data from the logcat to build a list"
        tmp = self.__get_logcat_results(split=True)
        entries = []
        for x in tmp:
            if x not in self.__previuos_results:
                entries.append(x)
        for x in self._result:
            for entry in entries:
                if entry.find(x[0]) != -1:
                    score = re.sub('.*score: |.*score is ', '', entry)
                    score = re.sub('[\t\r\n]+','', score)  # replace line symbols
                    res_doc.add_name(x[1])
                    res_doc.add_result(score)
                    break
