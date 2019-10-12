# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "1/21/2018 7:33 PM"

import os
import re
import sys
import types
import signal
import psutil
import platform
import subprocess
from time import sleep
from threading import Thread
from libs.core.logger import getSysLogger, getLogger
from libs.cmd.implement.exceptions import CommandExecuteError, TimeoutExpiredError
from libs.cmd.implement.constants import DEFAULT_WAIT_KILL_TIMEOUT, DEFAULT_VERBOSE_COMMAND
from libs.cmd.implement.constants import DEFAULT_COMMAND_TIMEOUT, DEFAULT_REMOVE_SPECIAL_SYMBOLS
from libs.cmd.implement.constants import CMD_LOG_FILE_NAME, CMD_LOG_NAME, RUN_COMMAND_THREAD_AS_DAEMON


class Command(Thread):
    """
    Execute any commands via PC terminal.

    Use standard python3 utility to execute commands.

    Supported OS:
        - Linux (Tested on Ubuntu 16 x64)
        - Windows (Tested on Windows 7 x64, 10 x64)
    """

    def __init__(self, logger=None, **kwargs):
        """
        Args:
            logger (logging, default None): Output logger to print in interactive mode
        """
        super(Command, self).__init__()
        # Thread.__init__(self)
        # daemon
        self.daemon = RUN_COMMAND_THREAD_AS_DAEMON

        # loggers
        self.logger = logger  # or getLogger(__file__)
        self.syslogger = getSysLogger()
        # special cmd logger. Logging all commands ant output
        self.cmdlogger = getLogger(CMD_LOG_NAME, file=CMD_LOG_FILE_NAME, propagate=False)

        # command properties
        self.__timeout = 0
        self.__interactive = False
        self.__interactive_filter = None
        self.__remove_line_symbols = False

        # command states
        self.__command = None  # last executed command
        self.__output = ''  # last command output
        self.__code = None  # last return code
        self.__process = None  # last Popen process
        self.__excerror = None  # last errors

    @property
    def lastcommand(self):
        """
        Last execute command

        "None" value mean command was not launched

        Returns:
             str or None
        """
        return self.__command

    @property
    def returncode(self):
        """
        Last command complete code.

        "None" value mean command was not completed or launched

        Returns:
             int or None
        """
        return self.__code

    @property
    def lasterror(self):
        """
        Last command error if exists

        Returns:
             last error or empty str
        """
        return self.__excerror

    def lastoutput(self):
        """
        Last command output

        Returns:
             str command output or empty str
        """
        return self.__output

    def __kill(self):
        """ Kill process """
        if self.__process.returncode is None:
            # try to kill via standard function
            self.__process.kill()
            # not killed yet
            if self.__process.returncode is None:
                # kill on Windows
                if 'windows' in platform.system().lower():
                    # kill all launched child process
                    for proc in psutil.process_iter(attrs=['name']):
                        if proc.ppid() == self.__process.pid:
                            os.kill(proc.pid, signal.SIGTERM)
                            self.cmdlogger.warning('KILL [%d %s] child process' % (proc.pid, proc.info['name']))
                # kill on Linux
                else:
                    os.killpg(os.getpgid(self.__process.pid), signal.SIGKILL)
                    self.cmdlogger.warning('[KILL PID: %d]...' % self.__process.pid)
                sleep(DEFAULT_WAIT_KILL_TIMEOUT)

    def __terminate(self):
        """ Terminate process """
        if platform.system().lower() == 'windows':
            self.__kill()
        else:
            if self.__process is not None:
                os.killpg(os.getpgid(self.__process.pid), signal.SIGTERM)
                self.cmdlogger.warning('[TERMINATE PID: %d]...' % self.__process.pid)

    def run(self):
        """ Launch command in thread """
        try:
            # process
            self.__process = subprocess.Popen(self.__command, bufsize=0,
                                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                              shell=False if 'windows' in platform.system().lower() else True,
                                              preexec_fn=os.setsid if 'linux' in platform.system().lower() else None)

            # print start
            self.cmdlogger.info('%s [PID: %s]' % (self.__command, self.__process.pid))

            # read output in real time
            while True:
                # decode string with ignore errors
                raw = self.__process.stdout.readline()

                # EOF
                if not raw:
                    break

                # output
                if self.__remove_line_symbols:
                    line = re.sub('[\t\r\n]+', ' ', raw.decode('utf-8', 'replace').rstrip())
                else:
                    line = raw.decode(encoding='utf-8', errors='replace').rstrip()

                # interactive
                if self.__interactive:
                    self.logger.info(line)
                self.cmdlogger.info(line)
                self.__output += line + ('\n' if not self.__remove_line_symbols else ' ')

                # filter function
                if self.__interactive_filter is not None:
                    self.__interactive_filter(line)

            # wait for normal complete
            self.__process.wait()
        except Exception:
            self.__excerror = sys.exc_info()

    def execute(self, command, **kwargs):
        """
        Execute command

        Args:
            command (str): Str command to execute

        Keyword args:
            timeout (int, default :data:`.constants.DEFAULT_COMMAND_TIMEOUT`): Command timeout. Should be integer > 0.
                Default timeout will be set if timeout <=0
            remove_line_symbols (bool, default :data:`.constants.DEFAULT_REMOVE_SPECIAL_SYMBOLS`): Remove line
                special symbols "\n\r\t" from each output line
            interactive (bool, default :data:`.constants.DEFAULT_VERBOSE_COMMAND`):
                Print command output in interactive mode
            interactive_filter (function, default None): Function to interaction with command output in real time mode.
                Should be a function or lambda and should receive str argument

        Raises:
            - TimeoutExpiredError when device not found and timeout expired
            - CommandExecuteError when command cannot be executed

        Returns:
            str command output
        """

        assert isinstance(command, str), 'Command to execute should be str !'

        # reset command states
        self.__command = command  # last executed command
        self.__output = ''  # last command output
        self.__code = None  # last return code
        self.__process = None  # last Popen process
        self.__excerror = None  # last errors

        # get execute properties
        # timeout
        self.__timeout = kwargs.get('timeout', DEFAULT_COMMAND_TIMEOUT)
        if self.__timeout <= 0:
            self.__timeout = DEFAULT_COMMAND_TIMEOUT
        # interactive mode
        self.__interactive = kwargs.get('interactive', DEFAULT_VERBOSE_COMMAND)
        if self.__interactive is True and self.logger is None:
            self.logger = getLogger(__file__)
        # check function
        self.__interactive_filter = kwargs.get('interactive_filter', None)
        if self.__interactive_filter is not None and not isinstance(self.__interactive_filter, types.FunctionType):
            raise CommandExecuteError('"interactive_filter" function should be a function or lambda !')
        # line symbols
        self.__remove_line_symbols = kwargs.get('remove_line_symbols', DEFAULT_REMOVE_SPECIAL_SYMBOLS)

        # start command
        self.start()

        # allow command with timeout only
        self.join(self.__timeout)

        # check execute error
        if self.__excerror:
            t, v, tb = self.__excerror
            self.__excerror = None
            # raise exception with traceback
            raise CommandExecuteError(v).with_traceback(tb)

        # check if alive thread
        if self.is_alive():
            self.cmdlogger.error('Timeout expired. Terminating process [%s] [PID: %d]...'
                                 % (self.__command, self.__process.pid))
            # try to kill
            self.__kill()
            self.join(DEFAULT_WAIT_KILL_TIMEOUT)
            # terminate. Terminate on windows is alias of kill
            if self.is_alive() and platform.system().lower() == 'linux':
                self.__terminate()
                self.join()
            # return code
            self.__code = self.__process.returncode
            raise TimeoutExpiredError('Timeout expired of [%s] command !' % self.__command)
        else:
            self.cmdlogger.error('[DONE PID: %d]...' % self.__process.pid)

        if not self.__process is None:
            # return code
            self.__code = self.__process.returncode
        return self.__output.strip()
