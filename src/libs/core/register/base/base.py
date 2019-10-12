# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "28/09/17 12:06"

import inspect
import hashlib
from libs.core.logger import getSysLogger
from .exceptions import ConfigAccessError, ConfigError


class Base:
    """
    Base config class.
    Logging all changes in attributes.
    """
    syslogger = getSysLogger()

    def __init__(self):
        pass

    def __setattr__(self, name, value):
        """
        Set config attribute and check if attribute is not locked.
        Also logging config changes.

        """
        frame = inspect.currentframe()
        self.syslogger.info('SET [%s.%s = %s]' % (frame.f_locals['self'].__class__.__name__, name, value))

        # check attribute locked
        if hasattr(self, ('_%s__lock__%s' % (self.__class__.__name__, name)).lower()):
            raise ConfigAccessError('[%s.%s] variable is locked and cannot be changed !'
                                    % (self.__class__.__name__, name))
        super(Base, self).__setattr__(name, value)

    def __getattribute__ (self, name):
        """
        Get config attribute and check if attribute is not locked.
        """
        if not name.startswith('_'):
            return self.__check_lock(name)
        return super(Base, self).__getattribute__(name)

    def __delattr__(self, name):
        frame = inspect.currentframe()
        self.syslogger.info('DEL [%s.%s]' % (frame.f_locals['self'].__class__.__name__, name))
        super(Base, self).__delattr__(name)

    def LOCK(self, name):
        """
        Lock variable to changes.

        Exceptions:
            ConfigError if variable to lock not found

        Args:
            name (str): Variable name to lock
        """
        if not hasattr(self, name):
            raise ConfigError('[%s] variable to lock not found in [%s] config !' % (name, self.__class__.__name__))

        _lock = ('_%s__lock__%s' % (self.__class__.__name__, name)).lower()
        setattr(self, _lock, hashlib.md5(str(getattr(self, name)).encode('utf-8')).hexdigest())

    def __check_lock(self, name):
        """
        Check if variable locked.

        Exceptions:
            ConfigAccessError if attempt changes to locked variable

        Args:
            name (str): Variable name to check
        """
        # check if variable locked
        _lock = ('_%s__lock__%s' % (self.__class__.__name__, name)).lower()
        if hasattr(self, _lock):
            _lock = getattr(self, _lock)
            if _lock != hashlib.md5(str(super(Base, self).__getattribute__(name)).encode('utf-8')).hexdigest():
                raise ConfigAccessError('[%s.%s] variable is locked and cannot be changed !'
                                        % (self.__class__.__name__, name))
        return super(Base, self).__getattribute__(name)
