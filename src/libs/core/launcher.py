# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/22/17 15:26"

import sys
import inspect
import asyncio
import platform
from .tools import Async
from config import CONFIG
from .results import Html
from .options.parser import Parser
from .unittest.runner import Runner
from libs.core.template import NAME
from libs.core.tools import Utility
from .unittest.config import RESULT_NAMES
from .unittest import ScanCases, ScanTests
from .exceptions import PrepareLauncherError
from optparse import OptionParser, SUPPRESS_HELP
from libs.core.logger import getLoggers, initLogger
from .options.exceptions import OptionsValidationError
from libs.core.exceptions import RuntimeInterruptError, InterruptByUser


class Launcher:
    """
    Main class to launch Framework core.
    """

    def __init__(self):
        self.logger, self.syslogger = getLoggers(__file__)

        # options parser
        self.parser = OptionParser(usage='python3 %prog [option] "args"',
                                   version='%s %s' % (CONFIG.PROJECT_NAME, CONFIG.PROJECT_VERSION),
                                   add_help_option=False)

        # add help and debug options
        self.parser.add_option('-h', '--help', dest='help', action="store_true", default=False, help="Print help.")
        self.parser.add_option('--debug', dest='debug', action="store_true", default=False, help=SUPPRESS_HELP)
        self.parser.add_option('--sdebug', dest='sdebug', action="store_true", default=False, help=SUPPRESS_HELP)

        # print framework version
        self.logger.newline()
        self.logger.table('=*', self.syslogger)
        self.logger.table(('Framework version: '.upper() + '%s' % CONFIG.PROJECT_VERSION, 'center'), self.syslogger)
        self.logger.table('=*', self.syslogger)
        self.logger.newline()

        # debug mode
        if '--debug' in sys.argv[1:]:
            CONFIG.SYSTEM.DEBUG = True
            CONFIG.SYSTEM.LOCK('DEBUG')

        # super debug mode
        if '--sdebug' in sys.argv[1:]:
            CONFIG.SYSTEM.DEBUG = True
            CONFIG.SYSTEM.SDEBUG = True
            CONFIG.SYSTEM.LOCK('DEBUG')
            CONFIG.SYSTEM.LOCK('SDEBUG')

        if CONFIG.SYSTEM.DEBUG:
            self.logger.table('#*', self.syslogger)
            self.logger.table('- *', self.syslogger)
            self.logger.table(('Framework configured to debug mode ! Some features may be disabled !'.upper(),
                               'center'), self.syslogger)
            self.logger.table('- *', self.syslogger)
            self.logger.table('#*', self.syslogger)
            self.logger.newline()

        # libs options
        self.libs_option = None
        # parsed launch options
        self.options = None

    def groups(self):
        """
        Scan all libs to find options and collect all options groups.
        """
        # scan project to libs options
        lib_parser = Parser(self.logger)
        self.libs_option = lib_parser.scan()

        # add all groups to option parser
        remove = []
        for opt in self.libs_option:
            try:
                group = opt.group(self.parser)
                group = group if isinstance(group, list) else [group]
                for grp in group:
                    self.parser.add_option_group(grp)
            except Exception as e:
                remove.append(opt)
                if CONFIG.SYSTEM.DEBUG is True:
                    raise
                self.syslogger.exception(e)
                self.logger.error('Options group from %s module cannot be got !'
                                  % NAME.safe_substitute(name=opt.fullname))

        # remove broken options classes
        for x in remove:
            self.syslogger.warning('Removing broken %s options module...' % NAME.safe_substitute(name=x.fullname))
            self.libs_option.remove(x)
            self.syslogger.done()

        # parse options
        self.options, args = self.parser.parse_args()

    def main(self):
        """
        Main function to launch Framework.

        Raises:
            :class:`OptionsValidationError`: If error happened during validation launch options.
        """
        try:
            # collect groups
            self.groups()

            # help option
            if self.options.help is True:
                self.logger.newline()
                self.parser.print_help()
                return

            # just create new event loop
            Async.get_event_loop()
            # load available tests
            asyncio.gather(asyncio.async(ScanTests().load_tests(self.libs_option)))

            # option validate tasks
            self.validate()

            # validate options and prepare tests and search device
            if self.sync() is True:
                # initialize Framework
                self.initialize()
                # launch tests
                self.launch()
                # complete Framework activity
                self.complete()

        except Exception as e:
            self.syslogger.exception(e)
            # don't raise exception for RuntimeInterruptError
            if not isinstance(e, RuntimeInterruptError):
                # raise exception in debug mode only
                if CONFIG.SYSTEM.DEBUG is True:
                    raise PrepareLauncherError(e) from e

            # just print message in non debug mode
            msg = Utility.error_to_message(e)
            if msg != '%s: ' % e.__class__.__name__:
                self.logger.newline()
                self.logger.error(msg, self.syslogger)

    def validate(self):
        """
        Create async tasks of validate options modules
        """
        async def opt_validate(_opt, _options):
            _opt.validate(_options)

        for opt in self.libs_option:
            self.syslogger.info('Validate "%s" options module...' % opt.fullname)
            # async validate function
            if 'validate' in opt.REGISTERED:
                if inspect.iscoroutinefunction(opt.validate):
                    asyncio.gather(asyncio.async(opt.validate(self.options)))
                else:  # not async validate function
                    asyncio.gather(asyncio.async(opt_validate(opt, self.options)))
            else:
                raise OptionsValidationError('No one of "validate" or "async_validate" functions were not specified '
                                             + 'for %s options module !' % NAME.safe_substitute(name=opt.fullname))

    def sync(self):
        """
        Wait for all async functions to prepare framework to launch
        """
        # scan tests in project
        unit_scan = ScanCases(self.logger)

        # get event loop
        event_loop = Async.get_event_loop()
        # create async tasks
        tasks = asyncio.gather(*asyncio.Task.all_tasks(loop=event_loop),  # get all soon tasks
                               asyncio.async(unit_scan.scan()))  # scan unit tests task

        # add empty exception handler
        Async.add_error_handler(event_loop)
        # run loop
        try:
            # wait complete all tasks
            event_loop.run_until_complete(tasks)
        except Exception as e:
            self.syslogger.exception(e)
            # if CONFIG.SYSTEM.DEBUG:
            #     self.logger.exception(e)
            raise
        finally:
            Async.close_loop(event_loop)
        return True

    def initialize(self):
        """
        Initialize Framework:
            - Get device information and add it to CONFIG
            - Initialize logger (make log folder, move all created files to new folder)
            - Execute :func:`Options.setup_frame()` function for all libs options
        """
        log_name = '_'.join(x['name'] + '-' + '-'.join(y['name'] for y in x['suites'])
                            for x in CONFIG.UNITTEST.SELECTED_TEST_CASES)
        if CONFIG.DEVICE.DEVICE_NAME != '':
            log_name = '%s_%s_%s_%s_%s' % (CONFIG.DEVICE.SERIAL,
                                           CONFIG.DEVICE.DEVICE_NAME or 'undefined',
                                           CONFIG.DEVICE.BUILD_TYPE or 'undefined',
                                           CONFIG.DEVICE.BUILD_VERSION or 'undefined',
                                           log_name)
        else:
            log_name = '%s_%s' % (CONFIG.DEVICE.SERIAL, log_name)
        initLogger(log_name)

        self.syslogger.newline(self.syslogger)
        self.syslogger.info('Framework was initialized !')
        self.syslogger.newline(self.syslogger)

        # Execute all "setup_frame" functions from libs options
        for opt in self.libs_option:
            if 'setup_frame' in opt.REGISTERED:
                self.syslogger.info('Execute "setup_frame" of %s options module...'
                                    % NAME.safe_substitute(name=opt.fullname))
                opt.setup_frame()
                self.syslogger.done()

    def launch(self):
        """
        Launch all Tests
        """
        # keep launch options
        CONFIG.UNITTEST.__USED_OPTIONS__ = ' '.join([x if len(x.split(',')) == 1 or len(x.split(';')) == 1
                                                     else "%s" % x for x in sys.argv[1:]])

        # launch tests
        try:
            runner = Runner(libs_options=self.libs_option)
            runner.launch()
        except InterruptByUser:
            if CONFIG.TEST.NOTIFICATION_CLASS is not None:
                answer = input("Test execution was interrupted by user. "
                               "Would you like to send email notify ? (y/n)")
                # clear Email class if no need send report
                if len(answer) != 0 and (answer[0] == 'n' or answer[0] == 'N'):
                    CONFIG.TEST.NOTIFICATION_CLASS = None
        except Exception as e:
            Utility.print_error(e, self.logger)
        finally:
            # get email sender
            if CONFIG.TEST.NOTIFICATION_CLASS is not None:
                # generate result email report
                html = Html.print_results(logger=self.logger, fail_traceback=True)
                # add test info
                text = '<b>Arguments:</b> %s %s<br>' % (sys.argv[0], CONFIG.UNITTEST.__USED_OPTIONS__)
                tmp = [x['name'] for x in CONFIG.UNITTEST.SELECTED_TEST_CASES]
                text += '<b>TestCase%s:</b> %s<br>' % ('s' if len(tmp) > 1 else '', ', '.join(tmp))
                tmp = [y['name'] for x in CONFIG.UNITTEST.SELECTED_TEST_CASES for y in x['suites']]
                text += '<b>TestSuite%s:</b> %s<br>' % ('s' if len(tmp) > 1 else '', ', '.join(tmp))
                text += '<b>Device:</b> %s - %s<br>' % (CONFIG.DEVICE.DEVICE_NAME or 'undefined', CONFIG.DEVICE.SERIAL)
                text += ('<b>Switchboard:</b> %s [%s]<br>' % (CONFIG.SWITCH.CLASS.__CLASS__.__NAME__,
                                                              CONFIG.SWITCH.SERIAL)) \
                    if CONFIG.SWITCH.CLASS is not None else ''
                # text += '<b>Preset:</b> %s<br>' % CONFIG.SYSTEM.PRESETS
                text += ('<b>Build fingerprint:</b> %s<br>' % CONFIG.DEVICE.BUILD_FINGERPRINT) \
                    if CONFIG.DEVICE.BUILD_FINGERPRINT != '' else ''
                text += ('<b>Comment:</b> %s<br>' % CONFIG.TEST.NOTIFICATION_COMMENT) \
                    if CONFIG.TEST.NOTIFICATION_COMMENT != '' else ''
                text += '<b>System:</b> %s%s Python %s (%s)<br>' \
                        % ((platform.node()+' ') if 'linux' in platform.system().lower() else '', platform.system(),
                           platform.python_version(), platform.architecture()[0])
                text += '<b>Logs folder:</b> %s<br>' % CONFIG.SYSTEM.LOG_PATH

                # email subject
                subject = ', '.join(x['name'] for x in CONFIG.UNITTEST.SELECTED_TEST_CASES)
                subject += ' // %s' % (CONFIG.DEVICE.DEVICE_NAME.upper()
                                       if CONFIG.DEVICE.DEVICE_NAME != '' else 'undefined')
                subject += ' // %s' % (CONFIG.DEVICE.SERIAL if CONFIG.SWITCH.CLASS is None
                                       else '%s -> %s' % (CONFIG.SWITCH.SERIAL, CONFIG.DEVICE.SERIAL))
                subject += ' // %s_%s_%s' % (CONFIG.DEVICE.BUILD_PRODUCT or 'undefined',
                                             CONFIG.DEVICE.BUILD_TYPE or 'undefined',
                                             CONFIG.DEVICE.BUILD_VERSION or 'undefined')
                subject += (' // %s' % CONFIG.TEST.NOTIFICATION_COMMENT) \
                    if CONFIG.TEST.NOTIFICATION_COMMENT != '' else ''
                # send email
                CONFIG.TEST.NOTIFICATION_CLASS().send_email(subject=subject, text=text+html)
                # save html page to file for test
                # import os
                # with open(os.path.join(os.path.split(CONFIG.SYSTEM.LOG_PATH)[0], 'test.html'), 'w') as file:
                #     file.write(text + html)

    def complete(self):
        """
        Actions after all TestCases are completed 
        """
        # Execute all "teardown_frame" functions from libs options
        for opt in self.libs_option:
            if 'teardown_frame' in opt.REGISTERED:
                self.syslogger.info('Execute "teardown_frame" of %s options module...'
                                    % NAME.safe_substitute(name=opt.fullname))
                opt.teardown_frame()
                self.syslogger.done()

        # get exit status. Required for Jenkins
        ran = 0
        skipped = 0
        for c in CONFIG.UNITTEST.SELECTED_TEST_CASES:
            for s in c['suites']:
                ran += s['ran']
                for e in s['tests']:
                    for cycle in range(CONFIG.SYSTEM.TOTAL_CYCLES_GLOBAL):
                        if e['results'] is not None and len(e['results']) > cycle:
                            if e['results'][cycle]['result'] == RESULT_NAMES['skip']:
                                skipped += 1
                            if e['results'][cycle]['result'] == RESULT_NAMES['error'] or \
                                    e['results'][cycle]['result'] == RESULT_NAMES['fail'] or \
                                    e['results'][cycle]['result'] == RESULT_NAMES['unexpected']:
                                self.logger.debug('EXIT 1')
                                sys.exit(1)
        if ran == 0 or ran == skipped:
            self.logger.debug('EXIT 1')
            sys.exit(1)
        self.logger.debug('EXIT 0')
        sys.exit(0)
