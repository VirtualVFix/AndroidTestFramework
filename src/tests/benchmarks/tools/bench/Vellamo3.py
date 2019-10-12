# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 13, 2014 8:47:25 PM$"

import re
from config import CONFIG
from tests.exceptions import ResultsNotFoundError
from tests.benchmarks.tools.base import OnlineBenchmark


class Vellamo3(OnlineBenchmark):
    def __init__(self, attributes, serial):
        OnlineBenchmark.__init__(self, attributes, serial)
        self._pull = attributes['pull']
        self.failed_fields = attributes['failed_fields']
        
    def start(self):
        try: 
            self.sh('rm -r ' + self._pull + '*.html', errors=False, empty=True)
        except: 
            pass
        super(Vellamo3, self).start()

    def __pull_logs(self):
        raw_res = []
        lslist = [x.replace('\r', '').strip() for x in self.sh('ls {} | grep .html'.format(self._pull)).split('\n')
                  if x.strip() != '\n' and x.strip() != '']
        if len(lslist) == 0: raise ResultsNotFoundError('Vellamo HTML results not found.')
        postfix = '_{}_{}.html'.format(CONFIG.CURRENT_CYCLE, CONFIG.LOCAL_CURRENT_CYCLE)
        for x in lslist:
            self.logger.info('Pulling {} log...'.format(x))
            self.pull(self._pull + x, CONFIG.LOG_PATH + x[:-5]+postfix)
            with open(CONFIG.LOG_PATH + x[:-5]+postfix, 'rb') as file: 
                raw_res.append(file.read())
        return zip(lslist, raw_res)

    def collect_results(self, res_doc):
        raw_res_list = self.__pull_logs()
        for log, raw_res in raw_res_list:
            match = re.search('h2\sstyle.*?>([\w\s/.-]+)<.*?Score:.*?>([\d]+)</span>', raw_res, re.DOTALL|re.I)
            res_doc.add_name(str(match.group(1).split(' ')[2].strip())+' ['+log+']')
            res_doc.add_result(match.group(2))
            rows = re.findall('<div\sclass=\'bm\'>(.*?)</div>', raw_res, re.DOTALL|re.I)
            for row in rows:
                match = re.search('<span>([\w\s/\(\).-]+)<.*?>([\w.\s]+)</span>', row, re.DOTALL|re.I)                
                res_doc.add_name(match.group(1))
                # failed fields
                if match.group(1) in self.failed_fields and match.group(2).strip() in ['0', '']:
                    res_doc.add_result('Failed')
                    for x in self.failed_fields[match.group(1)]:
                        res_doc.add_name(x)
                        res_doc.add_result('')
                else: 
                    res_doc.add_result(match.group(2))
                    values = re.findall('<li\sstyle.*?([\w\s/.-]+):\s([\w.\s]+)</li>', row, re.DOTALL|re.I)
                    for value in values:
                        # skip Invalid CPU mode error in result
                        if 'Invalid CPU' in value[1]:
                            continue
                        # skip failed field
                        if value[0].lower() == 'failed':
                            continue
                        res_doc.add_name(value[0])
                        res_doc.add_result(value[1])
        self.sh('rm -r ' + self._pull + '*.html', errors=False)
