# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/20/17 16:54"

import types
from config import CONFIG
from functools import wraps
from libs.core.logger import getLogger, getSysLogger


def Deprecated(func):
    """
    Decorator to mark function as deprecated.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = getLogger(func.__name__)
        logger.warning('"%s" is deprecated and can be removed in future update !' % func.__name__)
        return func(*args, **kwargs)

    return wrapper


def NotImplemented(func):
    """
    Decorator to mark function as not implemented.

    Raises:
        NotImplementedError:  Exception will raise when function in use
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        raise NotImplementedError('"%s" not implemented !' % func.__name__)

    return wrapper


def CatchException(msg='', logger=None, catch_except=None, raise_except=None, raise_in_debug=True, callback=None):
    """
    Decorator to catch specified in ``catch_except`` exception and raise ``raise_exception`` exception or
    :class:`Exception` from catch depends of arguments if Framework in debug mode or or print error message to
    ``logger`` and system logger otherwise. If ``raise_in_debug`` is False catch exception will be raised anyway.

    Args:
        msg (str): Message in exception on logger (Empty by default)
        logger (logging): Logger to send error message in non debug mode (None by default)
        catch_except (Exception): Exception need to catch (None by default)
        raise_except (Exception): Exception need to raise from catch (None by default)
        raise_in_debug (bool): Raises exception in debug mode only if True and raises exception anyway if False
        callback (func): Callback function if exception was catch. Callback should receive catch error as parameter
    """
    syslogger = getSysLogger()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except catch_except if catch_except is not None else Exception as e:
                syslogger.exception(e)
                # call callback
                if callback is not None and isinstance(callback, types.FunctionType):
                    callback(e)
                # raise required exception
                if raise_in_debug:
                    if CONFIG.SYSTEM.DEBUG is True:
                        raise raise_except(msg) if raise_except is not None else Exception(msg) from e
                else:
                    raise raise_except(msg) if raise_except is not None else Exception(msg) from e
                # print to logger
                if logger is not None:
                    logger.error(msg, syslogger)
        return wrapper
    return decorator
