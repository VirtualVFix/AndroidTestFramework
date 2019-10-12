# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

"""
Additional functions integrated to `logging.Logger` class when new logger created in :mod:`src.libs.core.logger` module.
"""

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "29/09/17 15:27"

import logging
from .config import LOCAL


def newline(self, *args, lines=1, level=logging.INFO):
    """
    Print empty line to all logger handlers via change handlers formatter.

    Args:
        *args (logging.Logger): Additional loggers to repeat action
        lines (int): Line counter
        level(int): Logger level
    """
    loggers = [x for x in args if isinstance(x, logging.Logger)]
    loggers.insert(0, self)

    for log in loggers:
        formats = []
        for x in log.handlers:
            formats.append(x.formatter)
            x.formatter = logging.Formatter(fmt=LOCAL.BLANK_LOGGER_FORMAT)

        for i in range(lines):
            log.log(level, '')

        for i, x in enumerate(log.handlers):
            x.formatter = formats[i]


def info(self, msg, *args, **kwargs):
    """
    Print INFO massage to current logger and all additional loggers specified as function parameters.

    Also function add **_last_message** attribute to loggers. This attribute uses in :func:`lastmsg` function.

    Args:
        msg (str): Logger massage
        *args (logging.Logger): Additional loggers to print

    Usage:

    .. code-block:: python

        import logging
        from core import getLogger, getSysLogger
        syslogger = getSysLogger()
        logger = getLoggger(__file__)
        logger2 = getLoggger('custom', custom.log)

        logger.info('spam message', logger2, syslogger)
    """
    setattr(self, '_last_message', msg)
    self._log(logging.INFO, msg, None, **kwargs)
    for x in args:
        if isinstance(x, logging.Logger):
            setattr(x, '_last_message', msg)
            if x.level <= logging.INFO:
                x._log(logging.INFO, msg, None, **kwargs)


def debug(self, msg, *args, **kwargs):
    """
    Print DEBUG massage to current logger and all additional loggers specified as function parameters.

    Also function add **_last_message** attribute to loggers. This attribute uses in :func:`lastmsg` function.

    Args:
        msg (str): Logger massage
        *args (logging.Logger): Additional loggers to print
    """
    setattr(self, '_last_message', msg)
    self._log(logging.DEBUG, msg, None, **kwargs)
    for x in args:
        if isinstance(x, logging.Logger):
            setattr(x, '_last_message', msg)
            if x.level <= logging.DEBUG:
                x._log(logging.DEBUG, msg, None, **kwargs)


def warning(self, msg, *args, **kwargs):
    """
    Print WARNING massage to current logger and all additional loggers specified as function parameters.

    Also function add **_last_message** attribute to loggers. This attribute uses in :func:`lastmsg` function.

    Args:
        msg (str): Logger massage
        *args (logging.Logger): Additional loggers to print
    """
    setattr(self, '_last_message', msg)
    self._log(logging.WARNING, msg, None, **kwargs)
    for x in args:
        if isinstance(x, logging.Logger):
            setattr(x, '_last_message', msg)
            if x.level <= logging.WARNING:
                x._log(logging.WARNING, msg, None, **kwargs)


def error(self, msg, *args, **kwargs):
    """
    Print ERROR massage to current logger and all additional loggers specified as function parameters.

    Also function add **_last_message** attribute to loggers. This attribute uses in :func:`lastmsg` function.

    Args:
        msg (str): Logger massage
        *args (logging.Logger): Additional loggers to print
    """
    setattr(self, '_last_message', msg)
    self._log(logging.ERROR, msg, None, **kwargs)
    for x in args:
        if isinstance(x, logging.Logger):
            setattr(x, '_last_message', msg)
            if x.level <= logging.ERROR:
                x._log(logging.ERROR, msg, None, **kwargs)


def exception(self, msg, *args, **kwargs):
    """
    Print EXCEPTION traceback to current logger and all additional loggers specified as function parameters.

    Also function add **_last_message** attribute to loggers. This attribute uses in :func:`lastmsg` function.

    Args:
        msg (str): Logger massage
        *args (logging.Logger): Additional loggers to print
    """
    setattr(self, '_last_message', msg)
    self._log(logging.ERROR, msg, None, **kwargs, exc_info=True)
    for x in args:
        if isinstance(x, logging.Logger):
            setattr(x, '_last_message', msg)
            if x.level <= logging.ERROR:
                x._log(logging.ERROR, msg, None, **kwargs, exc_info=True)


def critical(self, msg, *args, **kwargs):
    """
    Print CITICAL massage to current logger and all additional loggers specified as function parameters.

    Also function add **_last_message** attribute to loggers. This attribute uses in :func:`lastmsg` function.

    Args:
        msg (str): Logger massage
        *args (logging.Logger): Additional loggers to print
    """

    setattr(self, '_last_message', msg)
    if self.isEnabledFor(logging.CRITICAL):
        self._log(logging.CRITICAL, msg, None, **kwargs)
    for x in args:
        if isinstance(x, logging.Logger):
            setattr(x, '_last_message', msg)
            if x.level <= logging.CRITICAL and x.isEnabledFor(logging.CRITICAL):
                x._log(logging.CRITICAL, msg, None, **kwargs)


def lastmsg(self):
    """
    Return last logged message if **_lastmsg** attribute is available.

    Returns:
         last massage or empty str
    """
    return getattr(self, '_last_message', '')


def done(self, *args, level=logging.INFO):
    """
    Print "Done" massage.

    Args:
        *args (logging.Logger): Additional loggers to print
        level (int): Logger level
    """
    # duplicate code from spam function due to logging traceback system
    setattr(self, '_lastmsg', LOCAL.DONE_MESSAGE)
    self._log(level, LOCAL.DONE_MESSAGE, None)
    for x in args:
        if isinstance(x, logging.Logger):
            setattr(x, '_lastmsg', LOCAL.DONE_MESSAGE)
            x._log(level, LOCAL.DONE_MESSAGE, None)


def warnlist(self, msg, *args, propagate=True):
    """
    Print warning and keep it to ``CONFIG.SYSTEM.WARNINGS`` - those warning list prints after all tests

    Args:
         msg (str): Message
         *args (logging.Logger): Additional loggers to print
         propagate (bool): Print massage to loggers
    """
    from config import CONFIG
    CONFIG.SYSTEM.WARNINGS = msg
    if propagate is True:
        self.warning(msg, *args)


def jenkins(self, msg, *args, propagate=False, level=logging.INFO, secured=False):
    """
    Keep message to print it to Jenkins job or send by email.

    Args:
         msg (str): Message
         *args (logging.Logger): Additional loggers to print
         propagate (bool): Print massage to loggers
         level (int): Logger level
         secured (bool): Is message secured. Secured messaged cannot be send via regular Email client.
    """
    from config import CONFIG
    CONFIG.SYSTEM.JENKINS = (msg, level, secured)
    if propagate is True:
        if level == logging.DEBUG:
            self.debug(msg, *args)
        elif level == logging.INFO:
            self.info(msg, *args)
        elif level == logging.WARNING:
            self.warning(msg, *args)
        elif level == logging.ERROR:
            self.error(msg, *args)
        elif level == logging.CRITICAL:
            self.critical(msg, *args)
