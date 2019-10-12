# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/19/17 16:42"


class Singleton(type):
    """
    Base class to setup any class as Singleton.
    Specify this class as metaclass.

    Example:

    .. code-block:: python

        class SingletonClass(metaclass=Singleton)
            pass
            
        or

        class SingletonClass:
            __metaclass__ = Singleton
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def SingletonDecorator(cls):
    """
    Decorator to setup any class as Singleton.

    Args:
        cls (class): decorated class

    Returns:
        cls instance

    Warning:
        Some subclass or decorated inside methods may lost docstring.
        Not recommended use this decorator with documented class.

    Example:

    .. code-block:: python

            @SingletonDecorator
            class SingletonClass:
                pass
    """

    class WrapperClass(cls):
        _instance = None  # class instance

        def __new__(cls, *args, **kwargs):
            if WrapperClass._instance is None:
                WrapperClass._instance = super(WrapperClass, cls).__new__(cls, *args, **kwargs)
                WrapperClass._instance._initialized = False  # make sure class was initialized once only
            return WrapperClass._instance

    def __init__(self, *args, **kwargs):
        if self._initialized: return
        super(WrapperClass, self).__init__(*args, **kwargs)
        self._initialized = True

    WrapperClass.__name__ = cls.__name__
    WrapperClass.__doc__ = cls.__doc__
    WrapperClass.__module__ = cls.__module__
    return WrapperClass
