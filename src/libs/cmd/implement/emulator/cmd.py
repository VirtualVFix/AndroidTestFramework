# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "03/18/18 15:00"

import re
import types
from string import Template
from ..base.base import Base
from libs.cmd.interface.cmd import Cmd as CmdImp
from libs.core.logger import getLogger, getSysLogger


class Command:
    """ Emulate command output """
    def __init__(self, logger=None, **kwargs):
        self._command = None
        self._code = None
        self._error = None
        self._output = ''

    @property
    def lastcommand(self):
        return self._command

    @property
    def returncode(self):
        return self._code

    @property
    def lasterror(self):
        return self._error

    def lastoutput(self):
        return self._output


class Cmd(Base, CmdImp):
    """
    Base emulator class
    """

    def __init__(self, logger=None, **kwargs):
        """
        Args:
            logger (logging, default None): Custom logger. New logger will be created when None.

        Keyword args:
            __emulator_replace_keys__ (dict): Keys with data to replace in Emulator templates
        """
        super(Cmd, self).__init__(logger=logger, **kwargs)
        self.logger = logger or getLogger(__file__)
        self.syslogger = getSysLogger()
        # logger for all command output via emulator
        self.__fakelogger = getLogger('emulator', 'emulator.log', propagate=False)

        # replace dictionary
        self.__replace_keys = kwargs.get('__emulator_replace_keys__', {})
        if 'SERIAL' not in self.__replace_keys:
            self.__replace_keys['SERIAL'] = self.serial

        # command executor emulation
        self.__command = None

    @property
    def command(self):
        return self.__command

    def __replaceEnvironment(self, response):
        """
        Replace environment variable in response

        Args:
             response (dict): Dictionary of available responses
        """
        resp = response
        for key in resp:
            if isinstance(resp[key], Template):
                resp[key] = resp[key].safe_substitute(self.__replace_keys)
        return resp

    def __execute(self, command, response, **kwargs):
        """
        Execute fake commands

        Args:
            command (str): Command to execute
            response (dict): Dictionary of available responses
        """
        resp = self.__replaceEnvironment(response)
        # response not found
        if command not in resp:
            out = '[%s] command emulation error: Emulator response not found !' % command
        else:
            if isinstance(resp[command], types.FunctionType) or  isinstance(resp[command], types.MethodType):
                out = resp[command](**kwargs)
            else:
                out = resp[command]
        self.__fakelogger.info('[%s]' % command)
        self.__fakelogger.info(out)
        return out

    def __call__(self, command, *args, **kwargs):
        """
        Execute any string command

        Args:
            command (str): Command to execute

        Keyword args:
            __emulator_replace_keys__ (dict): Additional keys with data to replace in Emulator templates.
            __emulator_command_response__ (str, Template or function): Special response for current command.
        """
        self.__command = Command()
        self.__command._command = command
        self.__command._code = -1
        # print('CMD: "%s"' % command, args, kwargs)

        # additional replace dictionaries
        keys = kwargs.get('__emulator_replace_keys__', {})
        for key in keys:
            self.__replace_keys[key] = keys[key]

        # special response
        special_resp = kwargs.get('__emulator_command_response__', None)

        # detect type of command request
        # adb shell request
        if re.search('^adb .*? shell', command, re.I):
            cmd = re.sub('^adb\s*(-s.*?)*shell\s', '', command, re.I).strip('"')
            if special_resp is not None:
                return self.__execute(cmd, {cmd: special_resp}, **kwargs)
            else:
                from .constants import SHELL_RESPONSE
                return self.__execute(cmd, SHELL_RESPONSE, **kwargs)
        # adb request
        elif re.search('^adb', command, re.I):
            cmd = re.sub('^adb\s*(-s\s.*?\s)*', '', command, re.I)
            if special_resp is not None:
                return self.__execute(cmd, {cmd: special_resp}, **kwargs)
            else:
                from .constants import ADB_RESPONSE
                return self.__execute(cmd, ADB_RESPONSE, **kwargs)
        # fastboot request
        elif re.search('^fastboot', command, re.I):
            cmd = re.sub('^fastboot\s*(-s\s.*?\s)*', '', command, re.I)
            if special_resp is not None:
                return self.__execute(cmd, {cmd: special_resp}, **kwargs)
            else:
                from .constants import FATBOOT_RESPONSE
                return self.__execute(cmd, FATBOOT_RESPONSE, **kwargs)
        # cmd request
        else:
            if special_resp is not None:
                return self.__execute(command, {command: special_resp}, **kwargs)
            else:
                from .constants import CMD_RESPONSE
                return self.__execute(command, CMD_RESPONSE, **kwargs)
