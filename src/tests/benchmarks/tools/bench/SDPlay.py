# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 13, 2014 12:22:31 AM$"

import os
import csv
from config import CONFIG
from tests.benchmarks.tools.base import App
from tests.exceptions import ResultsNotFoundError


class SDPlay(App):
    """ SDPlay bench """
    def __init__(self, attributes, serial):
        App.__init__(self, attributes, serial)
        self._pull = attributes['pull']
        
    def __pull_logs(self):
        raw_res = []
        list = [x.replace('\r', '').strip() for x in self.sh('ls {} | grep .csv'.format(self._pull)).split('\n')
                if x != '\n' and x != '']
        logs = [x for x in list]
        if len(logs) == 0: raise ResultsNotFoundError('SDPlay results not found.')
        
        for x in logs:
            self.logger.info('Pulling {} log...'.format(x))
            self.pull(self._pull + x, CONFIG.SYSTEM.LOG_PATH)
            raw_res.append(os.path.join(CONFIG.SYSTEM.LOG_PATH, x))
        return raw_res

    def collect_results(self, res_doc):
        raw_res = self.__pull_logs()
        for file in raw_res:
            rows = []
            with open(file, newline='') as csvfile:
                for row in csv.DictReader(csvfile):
                    rows.append(row)
            list = sorted([(x, rows[len(rows)-1][x]) for x in rows[len(rows)-1]], key=lambda lm: lm[0])
            for x, v in list:
                res_doc.add_name(x[1:])
                res_doc.add_result(v)
