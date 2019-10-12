# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "13/10/17 20:54"

from config import CONFIG
from optparse import OptionGroup
from libs.core.options import Options
from libs.core.logger import getLogger, getSysLogger
from libs.core.exceptions import RuntimeInterruptError


class Test(Options):
    """
    Framework self test options.
    """

    def __init__(self):
        super(Test, self).__init__()

    def group(self, parser):
        group = OptionGroup(parser, 'Framework test parameters')
        group.add_option('--self-test', dest='self_test', action="store_true", default=False,
                         help='Execute self tests.')
        group.add_option('--stop-by-fail', dest='stop_by_fail', action="store_true", default=False,
                         help='Interrupt testing by first fail or error.')
        group.add_option('-c', '--cycles', dest='global_cycles', default=1,
                         help='Global Framework TestCase cycles. Should be integer in 1-9999 range.')
        return group

    @property
    def priority(self):
        return 999

    def validate(self, options):
        logger = getLogger("parser")
        syslogger = getSysLogger()

        # if options.case_list or options.suite_list or options.test_list:
        #     return

        # stop by fail
        if options.stop_by_fail is True:
            CONFIG.UNITTEST.INTERRUPT_BY_FAIL = True

        # self test mode
        if options.self_test is True:
            CONFIG.UNITTEST.SELF_TEST = True
            # logger.table('#*', syslogger)
            logger.table('- *', syslogger)
            logger.table(('Framework configured to self testing !'.upper(), 'center'), syslogger)
            logger.table('- *', syslogger)
            # logger.table('#*', syslogger)

        # Global test cycles
        if options.global_cycles:
            try:
                CONFIG.SYSTEM.TOTAL_CYCLES_GLOBAL = int(options.global_cycles)
                if CONFIG.SYSTEM.TOTAL_CYCLES_GLOBAL < 0:
                    raise RuntimeInterruptError('[--cycles] option should be integer >= 0 !')
            except Exception as e:
                syslogger.exception(e)
                raise RuntimeInterruptError(e)

        # lock changes
        CONFIG.UNITTEST.LOCK('SELF_TEST')
        CONFIG.SYSTEM.LOCK('TOTAL_CYCLES_GLOBAL')
        CONFIG.UNITTEST.LOCK('INTERRUPT_BY_FAIL')
