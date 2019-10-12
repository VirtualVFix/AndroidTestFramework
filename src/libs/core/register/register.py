# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/19/17 14:35"
__version__ = '0.0.12 dev'

import os
import inspect
import platform
from .test import Test
import importlib.machinery
from .device import Device
from .switch import Switch
from .system import System
from .jenkins import Jenkins
from .unittest import Unittest
from .database import Database
from ..singleton import Singleton
from libs.core.template import NAME
from ..logger import getSysLogger, getLogger
from libs.core.register.base.exceptions import ConfigError, ConfigAccessError


class Register(metaclass=Singleton):
    """
    System singleton configuration file.
    Keeps all static and dynamic framework configuration.
    All changes in config are logged.

    Register separated to different sub configs:
        - DEVICE:   Device settings and properties
        - SYSTEM:   System framework settings
        - UNITTEST: Unittest settings like test query and test results
        - SWITCH:   Switchboard settings if available
        - TEST:     Test settings. Uses in tests
        - JENKINS:  Jenkins settings
        - DATABASE: DataBase settings

    Note:
        Register should be import from `config.py` file by command **from config import CONFIG**
        and available from any place in framework. Default register sub configs settings are stored in default
        and external config files (See also: :func:`__init__`).

    Warning:
        Changes inside ``Register`` not allowed !

    Raises:
         ConfigAccessError: When try change or add any property inside ``Register``

    Usage:

    .. code-block:: python

        from config import CONFIG
        print(CONFIG.DEVICE.SERIAL)
    """

    #: default config (filename, classname)
    DEFAULT_CONFIG = ('config.py', 'DefaultConfig')
    # --------------------------------------------------------------------------
    # Framework core settings. Cannot be override or changed
    # --------------------------------------------------------------------------
    #: Framework version
    PROJECT_VERSION = __version__
    #: Framework name
    PROJECT_NAME = 'AndroidTestFramework'
    #: Project files extension. Should be tuple
    PROJECT_FILE_EXTENSIONS = ('.py', '.red')
    #: Project launch option postfix
    PROJECT_OPTIONS_FOLDER = '__opt__'
    #: Project unittest folder for framework self testS
    PROJECT_SELFTEST_FOLDER = '__test__'
    #: Project libs folder name
    PROJECT_LIBS_FOLDER = 'libs'
    #: Project logs folder name
    PROJECT_LOGS_FOLDER = 'logs'
    #: Project core folder name
    PROJECT_CORE_FOLDER = 'core'
    #: Project test folder name
    PROJECT_TESTS_FOLDER = 'tests'
    #: Project test suite folder name
    PROJECT_TESTS_SUITE_FOLDER = 'suites'
    #: Project test toolkit folder name
    PROJECT_TEST_TOOLS_FOLDER = 'tools'
    #: Project encrypt importer name
    PROJECT_ENCRYPT_IMPORTER = 'RedImport'
    #: Project suite.list file name for TestCase default TestSuites
    PROJECT_SUITE_LIST_FILE_NAME = 'suite.list'
    # --------------------------------------------------------------------------

    # config loggers
    logger = getLogger(__file__)
    syslogger = getSysLogger()

    def __init__(self):
        """
        Register during initializing search default and external config
        and override (when self.SYSTEM.EXTERNAL_CONFIG_COMBINE_WITH_MAIN = False) or combine attributes in sub configs.

        File and class name of default config stored in `self.DEFAULT_CONFIG` variable. File and name of external config
        should be specified in `SYSTEM.EXTERNAL_CONFIG` variable loaded from default config.

        Default and external configs may be stored by OS environment variable path specified
        in `SYSTEM.ENVIRONMENT_VARIABLE`.

        Default path for configs (`$FRAMEHOME` - is framework directory):
            - `$FRAMEHOME/src/` - for default config
            - `$FRAMEHOME/` - for external config
        """
        self.__system = System()    # system config
        self.__device = None        # device config
        self.__unittest = None      # unittest config
        self.__switch = None        # switchboard config
        self.__test = None          # test config. Resets each test.
        self.__jenkins = None       # jenkins config
        self.__database = None      # date base config

        # replace settings from default and external config
        # local config path
        path_dirs = [self.SYSTEM.ROOT_DIR,                    # root dir folder
                     os.path.split(self.SYSTEM.ROOT_DIR)[0]]  # add parent of root dir
        # config files. add default config file
        configs = [self.DEFAULT_CONFIG]

        # logging python version
        self.syslogger.info('%s %s Python %s %s' % (platform.node(), platform.system(), platform.python_version(),
                                                    platform.architecture()[0]))

        # scan config files
        while len(configs) > 0:
            try:
                # add path from environment variable
                if hasattr(self.SYSTEM, 'ENVIRONMENT_VARIABLE') \
                        and self.SYSTEM.ENVIRONMENT_VARIABLE in os.environ:
                    # scan environment variables
                    for x in reversed(os.environ[self.SYSTEM.ENVIRONMENT_VARIABLE]
                                              .split(';' if 'windows' in platform.system().lower() else ':')):
                        if x != '':
                            path_dirs.insert(0, x)

                # scan folders
                for path in path_dirs:
                    file = os.path.join(path, configs[0][0])

                    # config is n/a
                    if not os.path.exists(file):
                        self.syslogger.error('"%s" config not found in "%s" directory !' % (configs[0][0], path))
                        continue

                    # load config module
                    self.logger.info('Loading config file: %s...' % file, self.syslogger)
                    loader = importlib.machinery.SourceFileLoader('registerloader', file)
                    mod = loader.load_module()

                    # class is n/a
                    if not hasattr(mod, configs[0][1]):
                        self.logger.error('"%s" class not found in "%s" config' % (configs[0][1], configs[0][0]),
                                          self.syslogger)
                        continue

                    # get config class
                    cls = getattr(mod, configs[0][1])

                    # get all members
                    sub_conf = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))
                    sub_conf = [x for x in sub_conf if not x[0].startswith('_')]

                    for sub_name, sub_cls in sub_conf:
                        sub_name = sub_name.upper()

                        # sub config is n/a in register
                        if not hasattr(self, sub_name):
                            self.logger.error('Sub config "%s" from "%s" not found in register !'
                                              % (sub_name, cls.__name__), self.syslogger)
                            continue

                        # sub config variables
                        local_attributes = inspect.getmembers(sub_cls, lambda a: not (inspect.isroutine(a)))
                        local_attributes = [x for x in local_attributes if not x[0].startswith('_')]

                        for local_name, local_att in local_attributes:
                            # just add attribute if it not found in main config
                            if not hasattr(getattr(self, sub_name), local_name):
                                setattr(getattr(self, sub_name), local_name, local_att)
                                continue

                            # set attribute according to type and combine option
                            current = getattr(getattr(self, sub_name), local_name)
                            if current is None or type(local_att) == type(current):
                                # not combine mode. Just replace settings
                                if not hasattr(self.SYSTEM, 'EXTERNAL_CONFIG_COMBINE_WITH_MAIN') or \
                                        not self.SYSTEM.EXTERNAL_CONFIG_COMBINE_WITH_MAIN:
                                    setattr(getattr(self, sub_name), local_name, local_att)
                                else:
                                    # combine main and local config options with local config priority
                                    # use not subscriptable and string options from local config
                                    if current is None or isinstance(current, (str, int, float, bool)):
                                        setattr(getattr(self, sub_name), local_name, local_att)
                                    # combine dict or list options
                                    elif isinstance(current, dict):
                                        for x in local_att.keys():
                                            current[x] = local_att[x]
                                        setattr(getattr(self, sub_name), local_name, current)
                                    elif isinstance(current, list):
                                        for x in local_att:
                                            if not x in current:
                                                current.append(x)
                                        setattr(getattr(self, sub_name), local_name, current)
                                    else:
                                        self.syslogger.error('Not supporter sub config attribute type: %s'
                                                             % type(local_att))
                            else:
                                self.syslogger.error('Rewrite configuration error: '
                                                     + 'Inconsistent variable type: "%s" required %s - found %s'
                                                     % (local_name, type(current), type(local_att)))
                    self.logger.done(self.syslogger)
                    break
            except Exception as e:
                self.logger.exception(e)
                self.logger.error("Rewrite configuration error: %s" % e, self.syslogger)
            finally:
                # add external config
                if configs[0] == self.DEFAULT_CONFIG and hasattr(self.SYSTEM, 'EXTERNAL_CONFIG') \
                        and isinstance(self.SYSTEM.EXTERNAL_CONFIG, tuple) and len(self.SYSTEM.EXTERNAL_CONFIG):
                    configs.append(self.SYSTEM.EXTERNAL_CONFIG)
                configs.remove(configs[0])

    def __setattr__(self, name, value):
        """
        Denies any changes in register from outside.
        Allows changes for sub configs only.
        Also keeps all sub configs changes in logs.
        """
        frame = inspect.currentframe()
        self.syslogger.info('SET [%s.%s = %s]' % (frame.f_locals['self'].__class__.__name__, name, value))

        # allow change in Register from __init__ function only
        if not name.startswith('_%s__' % self.__class__.__name__) or inspect.currentframe().f_back.f_code.co_name == '<module>':
            raise ConfigAccessError('Register property %s cannot be changed !' % NAME.safe_substitute(name=name))
        super(Register, self).__setattr__(name, value)

    def __delattr__(self, item):
        """
        Denies delete in register.
        """
        frame = inspect.currentframe()
        self.syslogger.error('DEL [%s.%s]' % (frame.f_locals['self'].__class__.__name__, item))
        raise ConfigAccessError('Register properties cannot be deleted !')

    @property
    def DEVICE(self):
        """
        Device config property.

        Returns:
            :class:`src.libs.core.register.device.Device`: Internal device config class
        """
        if self.__device is None:
            self.__device = Device()
        return self.__device

    @property
    def SWITCH(self):
        """
        Switch config property.

        Returns:
            :class:`src.libs.core.register.switch.Switch`: Internal switch config class
        """
        if self.__switch is None:
            self.__switch = Switch()
        return self.__switch

    @property
    def SYSTEM(self):
        """
        System config property.

        Returns:
            :class:`src.libs.core.register.system.System`: Internal system config class
        """
        return self.__system

    @property
    def UNITTEST(self):
        """
        Unittest config property.

        Returns:
            :class:`src.libs.core.register.unittest.Unittest`: Internal unittest config class
        """
        if self.__unittest is None:
            self.__unittest = Unittest()
        return self.__unittest

    @property
    def TEST(self):
        """
        Test config property.

        Returns:
            :class:`src.libs.core.register.test.Test`: Internal test config class
        """
        if self.__test is None:
            self.__test = Test()
        return self.__test

    @property
    def JENKINS(self):
        """
        Jenkins config property.

        Returns:
            :class:`src.libs.core.register.jenkins.Jenkins`: Internal jenkins config class
        """
        if self.__jenkins is None:
            self.__jenkins = Jenkins()
        return self.__jenkins

    @property
    def DATABASE(self):
        """
        Database config property.

        Returns:
            :class:`src.libs.core.register.database.Database`: Internal Database config class
        """
        if self.__database is None:
            self.__database = Database()
        return self.__database

    def __propertyByName(self, config, prop, name=None, key=None):
        """
        Get value from config by ``prop`` depends of ``name`` and ``key`` selectors.

        Args:
            config (str): Name of sub config when need find ``prop``
            prop (str): Property name selector. Should be member of ``obj`` class.
            name (str): Attribute of ``prop`` if it's `dict`
            key (str): Key in ``prop[``name``]`` if it's `dict`

        Returns:
            Depends of ``prop`` type, ``name`` and ``key`` parameters:
            If ``name`` and ``key`` is None:

                - ``prop`` value if it found in ``obj``

            If ``prop`` type is `dict` and ``name`` is not None:

                - ``prop[name]`` or ``prop['default']`` or None

            If ``prop`` type is `dict`, ``name`` and ``key`` is not None:

                - ``prop[name][key]`` if ``prop[name]`` is `dict` and None otherwise

        Raises:
            ConfigError: If property not found
        """
        if not hasattr(self, config):
            raise ConfigError('Config: "%s" not found.' % config)

        if not hasattr(getattr(self, config), prop):
            raise ConfigError('Property: "%s" not found in "%s" config.' % (prop, config))

        var = getattr(getattr(self, config), prop)
        if isinstance(var, dict):
            var = var[name] if name in var.keys() else var['default'] if 'default' in var.keys() else None
            if key is not None:
                var = var[key] if key in var.keys() else None
        return var

    def propertyByDevice(self, config, prop, name=None, key=None):
        """
        Get value from dictionary property by device ``name`` or `DEVICE.DEVICE_NAME` if ``name`` is None

        Returns:
            :function:'src.libs.core.register._Register__propertyByName': self.__propertyByName(obj, prop, device, key)

        """
        device = name.lower() if name is not None else self.DEVICE.DEVICE_NAME.lower().split('_')[0]
        return self.__propertyByName(config, prop, device, key)

    def propertyByPlatform(self, config, prop, platform=None, key=None):
        """
        Get value from dictionary property by device ``platform`` or `DEVICE.CPU_HW` if ``platform`` is None

        Returns:
            :function:'src.libs.core.register._Register__propertyByName': self.__propertyByName(obj, prop, device, key)

        """
        device = platform.lower() if not platform is None else self.DEVICE.CPU_HW.lower()
        return self.__propertyByName(config, prop, device, key)
