# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "10/16/17 14:09"

import os
import asyncio
import inspect
from config import CONFIG
from ..tools import Async
from .options import Options
from libs.core.tools import load_module
from .exceptions import OptionsParserError
from libs.core.logger import getLogger, getSysLogger
from .config import OPTION_CLASS_FUNCTIONS_TO_REGISTER


class Parser:
    """
    Parse Framework libs options.
    """

    def __init__(self, logger=None):
        self.logger = logger or getLogger(__file__)
        self.syslogger = getSysLogger()

    @staticmethod
    def convert_path_to_name(path):
        """
        Convert file path to full import lib name
        """
        tmp = path.replace(CONFIG.SYSTEM.ROOT_DIR, '').replace(os.sep, '.')[1:]
        return tmp[:tmp.rfind('.')]

    def scan(self):
        """
        Scan project to find **__opt__** folders with option class inheritance from :class:`Options`
        to generate options list.

        Returns:
            list[module]: List with all loaded modules from **__opt__** folder

        Raises:
            :class:`OptionsParserError` when problem with import options found
        """

        result = []
        core = os.path.join(os.path.join(CONFIG.SYSTEM.ROOT_DIR, CONFIG.PROJECT_LIBS_FOLDER),
                            CONFIG.PROJECT_CORE_FOLDER)

        # wait core package
        async def wait_core(path):
            if not path.startswith(core):
                await asyncio.sleep(0)

        # add options after core package only
        async def get_options(_root, _file):
            path = os.path.join(_root, _file)
            await wait_core(path)
            # load module
            try:
                mod = load_module('parser_%s' % _file, path)
                result.append(mod)
            except Exception as e:
                self.syslogger.exception(e)
                if CONFIG.SYSTEM.DEBUG is True:
                    raise
                self.logger.error('[%s] options module loading error' % self.convert_path_to_name(path))

        # get event loop
        event_loop = Async.get_event_loop()

        tasks = []
        # create async tasks
        self.logger.info('Search for launch options in libraries...')
        for root, _, files in os.walk(os.path.join(CONFIG.SYSTEM.ROOT_DIR, CONFIG.PROJECT_LIBS_FOLDER)):
            if root.endswith(CONFIG.PROJECT_OPTIONS_FOLDER):
                for file in sorted(files):
                    if file.endswith(CONFIG.PROJECT_FILE_EXTENSIONS) and not file.startswith('_'):
                        tasks.append(asyncio.ensure_future(get_options(root, file)))

        # generate module list
        if len(tasks) == 0:
            raise OptionsParserError('No any options found !')

        # run loop
        try:
            event_loop.run_until_complete(asyncio.wait(tasks))
        finally:
            event_loop.close()
        self.logger.done()

        return self.generate_options_list(result)

    def generate_options_list(self, module_list):
        """
        Check loaded module from scan and get option class.

        Args:
            module_list (list): List of modules found in **__opt__** folders in libraries

        Returns:
             list[class]: List of option classes inheritance from :class:`Options`

        Raises:
            :class:`OptionsParserError` If options class cannot be loaded or options **group** cannot be got.
        """
        result = []
        # generate options dicts with functions
        for x in module_list:
            try:
                obj = None
                # find option classes
                for name, cls in inspect.getmembers(x):
                    try:
                        if cls is not Options and issubclass(cls, Options):
                            obj = cls()
                            obj.path = x.__file__
                            obj.filename = os.path.split(x.__file__)[1]
                            obj.fullname = self.convert_path_to_name(x.__file__)
                            result.append(obj)
                            break
                    except TypeError:
                        pass  # ignore issubclass type errors

                if obj is None:
                    raise OptionsParserError('Options module has not "Options" class !')
            except Exception as e:
                self.syslogger.exception(e)
                if CONFIG.SYSTEM.DEBUG is True:
                    raise
                self.logger.error('[%s] options file will be ignored due error' % self.convert_path_to_name(x.__file__))
        return self.register_functions(self.order_by_priority(result))

    def register_functions(self, result):
        """
        Register additional function from options class.\n
        Create **REGISTERED** list of not empty optional functions.

        Note:
            Only registered functions may be executed during testing or Framework launch.

        Note:
             Only async function will be registered if both async and regular functions were overridden.

        Args:
            result (list): List of options classes

        Returns:
            Updated list of options classes with added register.
        """
        def empty_func():
            pass

        def empty_doc_func():
            """ doc """
            pass

        for cls in result:
            register = []
            for x in inspect.getmembers(cls):
                if inspect.ismethod(x[1]):
                    if x[0] in OPTION_CLASS_FUNCTIONS_TO_REGISTER:
                        # registering non empty function
                        if x[1].__code__.co_code != empty_func.__code__.co_code \
                                and x[1].__code__.co_code != empty_doc_func.__code__.co_code:
                            register.append(x[0])
                            self.syslogger.info('"%s" function was registered for "%s" options module'
                                                % (x[0], cls.fullname))
            cls.REGISTERED = register
            if len(register) == 0:
                self.syslogger.warning('No one of additional functions were registered for "%s" options module !'
                                       % cls.fullname)
        return result

    @staticmethod
    def order_by_priority(result):
        """
        Order list by **priority** option attribute.

        Args:
            result (list): List of options classes

        Returns:
            Ordered result list
        """
        tmp = []
        prev = ''
        for x in result:
            path = os.path.split(x.path)[0]
            if path != prev:
                tmp.append([x])
                prev = path
            else:
                tmp[len(tmp)-1].append(x)

        result = []
        for x in tmp:
            result += sorted(x, key=lambda k: k.priority)[::-1]
        return result
