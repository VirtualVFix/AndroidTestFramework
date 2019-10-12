# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "15/03/18 21:10"

import re
from functools import wraps
from ..constants import CMD_ERROR_PRINT_LINES
from ..exceptions import ObjectDoesNotExistError, CommandSyntaxError
from ..exceptions import ResultError, AccessDeniedError, CommandNotFoundError


def __raise_error(expt, out, index, msg=''):
    """
    Raise expt error and generate exception message according to parameters.

    Args:
        expt (subclass of Exception): Exception to raise
        out (str): Command output to add to Exception message
        index (int): Start index to cut output for error. Long message will be cut
            at index += :data:`constants.CMD_ERROR_PRINT_LINES` (Configured in **CMD_ERROR_PRINT_LINES**)
        msg (str, default ''): Additional message for error

    """
    lower = index - CMD_ERROR_PRINT_LINES
    upper = index + CMD_ERROR_PRINT_LINES
    tmp = out.split('\n')
    err = tmp[lower if lower > 0 else 0:upper]
    raise expt('%s%s%s%s' % (msg, '... ' if lower > 0 else '', '\n '.join(err), ' ...' if upper < len(tmp) - 1 else ''))


def AdbGuard(func):
    """
    Adb and Adb shell commands implementation execute guard.

    Keyword args:
        errors (bool, default True): Check errors is required
        empty (bool, default True): Allow empty command output
        error_message (str, default ''): Additional message when raise error
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # print('@@@', args, kwargs)
        # check errors
        errors = kwargs.get('errors', True)
        # Check if command may be empty
        empty = kwargs.get('empty', True)
        # get additional message
        error_message = kwargs.get('error_message', '')
        out = func(self, *args, **kwargs)

        # check if command output is empty
        if out is None or out.strip() == '':
            if empty:
                return out
            else:
                raise ResultError('%sOutput is empty.' % error_message)

        # check errors
        if errors:
            for i, line in enumerate(out.lower().split('\n')):
                if re.search('SecurityException|permission denied|permissions denied|not permitted|access denied'
                             + '|root user', line, re.I):
                    __raise_error(AccessDeniedError, out=out, index=i, msg=error_message)
                if re.search('\s+(\w+):\s+not found', line, re.I):
                    __raise_error(CommandNotFoundError, out=out, index=i, msg=error_message)
                if re.search('is not recognized as an internal or external command', line, re.I):
                    __raise_error(CommandNotFoundError, out=out, index=i, msg=error_message)
                if re.search('does not exist|no such file or directory', line, re.I):
                    __raise_error(ObjectDoesNotExistError, out=out, index=i, msg=error_message)
                if re.search('syntax error', line, re.I):
                    __raise_error(CommandSyntaxError, out=out, index=i, msg=error_message)
                if re.search('latest motorola fastboot', line, re.I):
                    raise ResultError('Latest Motorola fastboot is required !')
                if re.search('error|fail', line, re.I):
                    __raise_error(ResultError, out=out, index=i, msg=error_message)
        return out
    return wrapper
