# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/26/17 17:20"

import os
import re
import sys
import pytz
import types
import shutil
import logging
import datetime
from .table import table
from .config import LOCAL
from .exceptions import LoggerError
from libs.core.template import NAME
from .handler import FileHandlerWithCompress
from .utils import done, newline, warnlist, jenkins
from .utils import lastmsg, debug, info, error, exception, warning, critical


def initLogger(folder_name):
    """
    Initialize logger:

        - Create new logs directory
        - Close steam for each file handler which store files in temporary log folder
        - Remove file prefix and new if required
        - Change file path to new folder for each file handler
        - Move already created log files to new folder with new name with replaced prefix
    """
    try:
        syslogger = getSysLogger()

        from config import CONFIG
        if CONFIG.SYSTEM.LOG_PATH is None:
            CONFIG.SYSTEM.LOG_PATH = LOCAL.DEFAULT_LOGS_FOLDER

        # generate log name
        name = re.sub('[^\w\d_.-]','', folder_name)
        name = datetime.datetime.now(pytz.timezone(CONFIG.SYSTEM.TIMEZONE)).strftime(LOCAL.LOG_DIR_DATE_FORMAT) + name
        if len(name) > LOCAL.LOG_DIR_LENGTH_PATH:
            name = name[:LOCAL.LOG_DIR_LENGTH_PATH] + '...'
        CONFIG.SYSTEM.LOG_PATH = os.path.join(CONFIG.SYSTEM.LOG_PATH, name)

        # create log folder
        if not os.path.exists(CONFIG.SYSTEM.LOG_PATH):
            syslogger.info('Creating %s logs directory...' % NAME.safe_substitute(name=CONFIG.SYSTEM.LOG_PATH))
            os.mkdir(CONFIG.SYSTEM.LOG_PATH)
            syslogger.done()

        # find all file handlers, close steam and change file path
        files = []
        for x in logging.Logger.manager.loggerDict:
            logger = logging.Logger.manager.loggerDict[x]
            if hasattr(logger, 'handlers'):
                for x in logger.handlers:
                    if isinstance(x, logging.FileHandler):
                        if x.baseFilename.startswith(LOCAL.DEFAULT_LOGS_FOLDER):
                            if x.baseFilename not in files:
                                files.append(x.baseFilename)
                            x.close()
                            _name = '%s%s' % (CONFIG.SYSTEM.LOG_PREFIX,
                                              os.path.split(x.baseFilename)[1].replace(LOCAL.DEFAULT_FILE_PREFIX, ''))
                            x.baseFilename = os.path.join(CONFIG.SYSTEM.LOG_PATH, _name)

        # move logs files to new logs folder
        for x in files:
            # move log files
            try:
                _name = '%s%s' % (CONFIG.SYSTEM.LOG_PREFIX, os.path.split(x)[1].replace(LOCAL.DEFAULT_FILE_PREFIX, ''))
                shutil.move(x, os.path.join(CONFIG.SYSTEM.LOG_PATH, _name))
                syslogger.info('%s log file was moved to new logs folder !' % NAME.safe_substitute(name=x))
            except PermissionError as e:
                # copy file if it cannot be moved
                # logger.exception(e)
                syslogger.exception(e)
                with open(x, 'rb') as rfile:
                    with open(os.path.join(CONFIG.SYSTEM.LOG_PATH, _name), 'wb') as wfile:
                        wfile.writelines(rfile.readlines())
                # try to remove file
                try:
                    shutil.rmtree(x)
                except Exception as e:
                    # logger.exception(e)
                    syslogger.exception(e)
                    # Add file to remove list after Framework close
                    LOCAL.REMOVE_LIST.append(x)

        # mark logger as initialized
        LOCAL.INITIALIZED = True
        CONFIG.SYSTEM.INITIALIZED = True
        # lock options
        CONFIG.SYSTEM.LOCK('INITIALIZED')
        CONFIG.SYSTEM.LOCK('LOG_PREFIX')
        CONFIG.SYSTEM.LOCK('LOG_PATH')
    except Exception as e:
        raise LoggerError('Logger initialize error: %s' % e) from e


def tearDownLogger():
    """
    Logger clear function before Framework will be stopped
    """
    # Clear logs from remove list
    if len(LOCAL.REMOVE_LIST) > 0:
        # try to remove file
        for x in LOCAL.REMOVE_LIST:
            try:
                shutil.rmtree(x)
            except Exception:
                pass


def getLoggers(name, file=None, folder=None, propagate=True, level=None):
    """
    Get regular and system loggers. Use :func:`getLogger` and :func:'getSysLogger' functions to get loggers.

    Returns:
        (regular logger, system logger)
    """
    return getLogger(name, file, folder, propagate, level), getSysLogger()


def getSysLogger():
    """
    Get system logger.
    Use this logger if need logging any system information or errors.

    Returns:
         logging: System logger to `sys.log` file
    """
    return getLogger(LOCAL.SYS_LOGGER_FILE_NAME[:LOCAL.SYS_LOGGER_FILE_NAME.rfind('.')],
                     file=LOCAL.SYS_LOGGER_FILE_NAME, propagate=False, level=logging.DEBUG)


def getLogger(name, file=None, folder=None, propagate=True, level=None):
    """
    Get logger with ``name`` name.

    Args:
        name (str): Logger name. Recommended use `__file__` as logger name.
        file (str): Create file logger with ``file`` name.
        folder (str): Create subfolder in log directory.
        propagate (bool):
            If this evaluates to true, events logged to this logger will be passed to the handlers of higher level (ancestor)
            loggers, in addition to any handlers attached to this logger. Messages are passed directly to the ancestor
            loggers’ handlers - neither the level nor filters of the ancestor loggers in question are considered.
            If this evaluates to false, logging messages are not passed to the handlers of ancestor loggers.
            The constructor sets this attribute to True.
        level (int): Logger level. By default setups automatically according to Framework debug mode

    Note:
        If you attach a handler to a logger and one or more of its ancestors,
        it may emit the same record multiple times. In general, you should not need to attach a handler to more than one
        logger - if you just attach it to the appropriate logger which is highest in the logger hierarchy,
        then it will see all events logged by all descendant loggers, provided that their propagate setting is left set to True.
        A common scenario is to attach handlers only to the root logger, and to let propagation take care of the rest.

    Returns:
        logging: Logger with stream and/or file handler

    Example:

    .. code-block:: python

         from core import getLogger
         logger = getLoggger(__file__)
         logger.info('text')
         logger.newline()
    """
    # create logger
    logger = logging.getLogger(name if not name.endswith(LOCAL.FILE_EXTENSIONS)
                               else os.path.splitext(os.path.basename(name))[0])
    logger.handlers.clear()
    # if logger initialized
    if LOCAL.INITIALIZED is True:
        from config import CONFIG
        # stream formatter
        stream_formatter = LOCAL.CONSOLE_LOG_FORMAT if not CONFIG.JENKINS.INTEGRATE else LOCAL.JENKINS_LOG_FORMAT
        stream_date = LOCAL.CONSOLE_LOG_DATE_FORMAT if not CONFIG.JENKINS.INTEGRATE else LOCAL.JENKINS_LOG_DATE_FORMAT
        # log path
        log_path = CONFIG.SYSTEM.LOG_PATH
        log_prefix = CONFIG.SYSTEM.LOG_PREFIX if hasattr(CONFIG.SYSTEM, 'LOG_PREFIX') else ''
        # logger level
        logger.setLevel(level or (logging.DEBUG if CONFIG.SYSTEM.DEBUG or CONFIG.SYSTEM.SDEBUG else logging.INFO))
        # File size limit
        file_size_limit = CONFIG.SYSTEM.LOG_FILE_SIZE_LIMIT*1024*1024
    else:
        # stream formatter
        stream_formatter = LOCAL.CONSOLE_LOG_FORMAT
        stream_date = LOCAL.CONSOLE_LOG_DATE_FORMAT
        # log path
        log_path = LOCAL.DEFAULT_LOGS_FOLDER
        log_prefix = LOCAL.DEFAULT_FILE_PREFIX
        # logger level
        logger.setLevel(level or (logging.DEBUG if LOCAL.DEBUG else logging.INFO))
        # File size limit
        file_size_limit = 0

    # file logger
    if folder is not None:
        log_path = os.path.join(log_path, folder)

    # create folder if required
    if not os.path.exists(log_path):
        os.mkdir(log_path, 0o777)

    log_name = log_prefix + (file or LOCAL.DEFAULT_LOGGER_FILE_NAME)
    log_name = log_name + ('.log' if not log_name.endswith('.log') else '')
    # create file handler
    handler = FileHandlerWithCompress(os.path.join(log_path, log_name), maxBytes=file_size_limit, encoding='utf-8')
    # file formatter
    if file is not None:
        formatter = logging.Formatter(LOCAL.FILE_LOG_FORMAT, datefmt=LOCAL.FILE_LOG_DATE_FORMAT)
    else:  # formatter for default file
        formatter = logging.Formatter(stream_formatter, datefmt=stream_date)

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = propagate

    # console logger
    if propagate:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(stream_formatter, datefmt=stream_date)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = propagate

    # add extra functions
    # logger.spam = lambda self=logger, *args, **kwargs: spam(self, *args, **kwargs)
    # logger.done = lambda self=logger, *args, **kwargs: done(self, *args, **kwargs)
    # logger.table = lambda self=logger, *args, **kwargs: table(self, *args, **kwargs)
    # logger.newline = lambda self=logger, *args, **kwargs: newline(self, *args, **kwargs)
    # logger.jenkins = lambda self=logger, *args, **kwargs: jenkins(self, *args, **kwargs)
    # logger.warnlist = lambda self=logger, *args, **kwargs: warnlist(self, *args, **kwargs)
    # logger.lastmessage = lambda self=logger, *args, **kwargs: lastmessage(self)
    logger.info = types.MethodType(info, logger)
    logger.debug = types.MethodType(debug, logger)
    logger.error = types.MethodType(error, logger)
    logger.warn = types.MethodType(warning, logger)
    logger.warning = types.MethodType(warning, logger)
    logger.critical = types.MethodType(critical, logger)
    logger.exception = types.MethodType(exception, logger)
    logger.done = types.MethodType(done, logger)
    logger.table = types.MethodType(table, logger)
    logger.newline = types.MethodType(newline, logger)
    logger.jenkins = types.MethodType(jenkins, logger)
    logger.warnlist = types.MethodType(warnlist, logger)
    logger.warninglist = types.MethodType(warnlist, logger)
    logger.lastmsg = types.MethodType(lastmsg, logger)
    logger.lastmessage = types.MethodType(lastmsg, logger)

    return logger


# configure logger to unbuffered stdout and stderr
if hasattr(sys.stdout, 'logger') and getattr(sys.stdout, 'logger') is None:
    sys.stdout.logger = getLogger('stdout', propagate=False)
if hasattr(sys.stderr, 'logger') and getattr(sys.stderr, 'logger') is None:
    sys.stdout.logger = getLogger('stderr', propagate=False)
