# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/22/17 14:23"

import re
import os
import asyncio
from config import CONFIG
from time import time, sleep
from .property import Property
from libs.core.template import NAME
from .implement.factory import Factory
from libs.core.logger import getLogger, getSysLogger
from .implement.constants import DEFAULT_SLEEP_FOR_WAIT_ADB
from .implement.exceptions import RemountFailedError, DeviceEnumeratedError
from libs.cmd.implement.exceptions import AccessDeniedError, ObjectDoesNotExistError
from .implement.constants import DEFAULT_FIRST_DEVICE_DETECT_TIMEOUT
from .implement.constants import DEFAULT_SLEEP_FOR_WAIT_SERVICE, DEFAULT_WAIT_SERVICE_TIMEOUT
from .implement.exceptions import TimeoutExpiredError, InconsistentStateError, CommandExecuteError
from .implement.constants import DEFAULT_SLEEP_FOR_WAIT_IDLE, DEFAULT_WINDOWS_THRESHOLD_FOR_DETECT_IDLE
from .implement.constants import DEFAULT_ADB_SERVER_KILL_ALLOWED, ADB_MODE_ALIASES, FASTBOOT_MODE_ALIASES
from .implement.constants import DEFAULT_PULL_TIMEOUT, DEFAULT_PUSH_TIMEOUT, DEFAULT_MANAGER_COMMAND_VERBOSE
from .implement.constants import DEFAULT_WAIT_DEVICE_TIMEOUT, DEFAULT_WAIT_ROOT_TIMEOUT, DEFAULT_REMOUNT_TIMEOUT


class Manager:
    """
    Class combine management of all main utilities like
    ``adb``, ``adb shell``, ``fastboot`` and PC terminal ``cmd``:
    """

    def __init__(self, serial=None, logger=None, **kwargs):
        """
        Args:
            logger (logging): Custom logger if need print output with one logger. New logger will be created if None.
            serial (str): Serial number of device. May be None (Default: None)

        Keyword args:
            general_type (str): General implementation type of all utilities (cmd, adb, adb shell and fastboot).
                Uses in factory method if special type not set.
            cmd_type (str): CMD implementation type for factory method
            adb_type (str): ADB implementation type for factory method
            shell_type (str): ADB SHELL implementation type for factory method
            fastboot_type (str): FASTBOOT implementation type for factory method

        .. code-block:: python

            mn = Manager(general_type = 'base',  # setup "Base" implementation for all utility
                         adb_type='tcp',         # setup "tcp" implementation for ADB
                         adb_shell_type='tcp')   # setup "tcp" implementation for ADB SHELL
        """
        self.logger = logger or getLogger(__file__)
        self.syslogger = getSysLogger()
        # chose utility implementation
        _type = kwargs.get('general_type', None)
        factory = Factory(serial=serial, logger=logger, **kwargs)
        # device serial number
        self.__serial = serial
        # pc terminal
        self.__cmd = factory.get_cmd(imp_type=kwargs.get('cmd_type', None) or _type, **kwargs)
        # adb utility
        self.__adb = factory.get_adb(imp_type=kwargs.get('adb_type', None) or _type, **kwargs)
        # adb shell utility
        self.__shell = factory.get_shell(imp_type=kwargs.get('shell_type', None) or _type, **kwargs)
        # fastboot utility
        self.__fastboot = factory.get_fastboot(imp_type=kwargs.get('fastboot_type', None) or _type, **kwargs)
        # device properties
        self.__properties = Property(manager=self, logger=self.logger)
        # Current mode. Used to fasted execute commands with out excess delays in same operations like "wait for device"
        self._current_mode = None

    @property
    def saved_mode(self):
        """
        Get current saved mode.
        Saved mode used to fasted execute commands without excess delays in same operations like "wait for device"

        Returns:
            str or None: self._current_mode if saved modes the same in "adb", "fastboot" and "shell" or None otherwise
        """
        if self._current_mode != self.adb.saved_mode \
                or self._current_mode != self.fastboot.saved_mode \
                or self._current_mode != self.shell.saved_mode:
            return None
        return self._current_mode

    @property
    def serial(self):
        """
        Device serial number property.

        Returns:
             str: Device serial number or None
        """
        return self.__serial

    @serial.setter
    def serial(self, value):
        """
        Device serial number setter.

        Args:
             value (str): Device serial number or None
        """
        self.__serial = value
        if self.__adb is not None:
            self.__adb.serial = self.__serial
        if self.__shell is not None:
            self.__shell.serial = self.__serial
        if self.__fastboot is not None:
            self.__fastboot.serial = self.__serial

    @property
    def cmd(self):
        """
        Get ``CMD`` terminal class.
        Allow to execute any ``CMD`` command if use as function *cmd('utils', 'arg1', 'arg2, ...)*
        or give access to ``CMD`` class functions if use as property *cmd.some_function()*
        """
        return self.__cmd

    @property
    def adb(self):
        """
        Get ``ADB`` utility class.
        Allow to execute any ``ADB`` command if use as function *adb('arg1', 'arg2', ...)*
        or give access to ``ADB`` class functions if use as property *adb.some_function()*
        """
        return self.__adb

    @property
    def shell(self):
        """
        Get ``ADB shell`` utility class.
        Allow to execute any ``ADB shell`` command if use as function *shell('command')*
        or give access to ``ADB shell`` class functions if use as property *shell.some_function()*
        """
        return self.__shell

    @property
    def sh(self):
        """
        Alias for :func:`shell` property.
        """
        return self.__shell

    @property
    def fastboot(self):
        """
        Get ``fastboot`` utility class.
        Allow to execute any ``fastboot`` command if use as function *fastboot('arg1', 'arg2, ...)*
        or give access to ``fastboot`` class functions if use as property *fastboot.some_function()*
        """
        return self.__fastboot

    @property
    def fb(self):
        """
        Alias for :func:`fastboot` property
        """
        return self.__fastboot

    @property
    def properties(self):
        """
        Get :class:`.cmd.property.Property` class
        """
        return self.__properties

    @property
    def prop(self):
        """
        Alias for :func:`properties` property
        """
        return self.__properties

    def __update_saved_mode(self, value):
        """
        Change saved mode.
        Saved mode used to fasted execute commands with out excess delays in same operations like "wait for device"

        Args:
            value (str or None): Mode name

        Allowed the following modes:
            - None - Mode not set
            - 'adb' - Saved in adb. Device was detected in ADB mode
            - 'fastboot' - Seved in fastboot. Device was detected in FASTBOOT mode
            - 'idle' - Saved in shell. Device was detected in ADB IDLE mode
            - 'service' - Saved in shell. Device was detected in ADB and services was loaded
        """
        self._current_mode = value
        self.adb._current_mode = value
        self.shell._current_mode = value
        self.fastboot._current_mode = value

    @staticmethod
    def _reduce_timeout(start_time, timeout):
        """
        Reduce timeout from *timeout* variable.
        Uses in multi commands functions which should have general timeout.

        Note:
            Minimal reducing to 1 second

        Args:
            start_time (float): Time when function was started
            timeout (int): Timeout to reduce

        Returns:
             timeout, time: reduced timeout and current time

        .. code-block:: python

            from time import time

            def test(self, timeout=10):
                start_time = time()
                self.action_with_timeout(timeout)
                timeout, start_time = self._reduce_timeout(start_time, timeout)
                self.other_action_with_timeout(timeout)
        """
        if timeout is None:
            return timeout, time()

        new_timeout = timeout - (time() - start_time)
        return new_timeout if new_timeout > 0 else 1, time()

    def root(self, timeout=DEFAULT_WAIT_ROOT_TIMEOUT, **kwargs) -> bool:
        """
        Request for root permissions

        Keyword args:
            verbose (bool, default :data:`.constants.DEFAULT_MANAGER_COMMAND_VERBOSE`): Print process to output
            timeout (int, default :data:`.constants.DEFAULT_WAIT_ROOT_TIMEOUT`): Timeout in seconds. One timeout
                for all actions inside.

        Returns:
            bool
        """
        verbose = kwargs.get('verbose', DEFAULT_MANAGER_COMMAND_VERBOSE)
        start_time = time()
        self.wait_for('adb', timeout=timeout, **kwargs)
        # reduce timeout
        timeout, start_time = self._reduce_timeout(start_time, timeout)
        out = self.adb('root', timeout=timeout, **kwargs)

        if re.search('product', out, re.I | re.DOTALL):
            CONFIG.DEVICE.IS_PRODUCT_BUILD = True
            self.logger.error(out, self.syslogger)
            return False
        elif not re.search('is already', out, re.I | re.DOTALL):
            if verbose:
                self.logger.info('Requesting root privileges...')
                # reduce timeout
                timeout, start_time = self._reduce_timeout(start_time, timeout)
            self.wait_for('adb', timeout=timeout, **kwargs)
            if verbose:
                self.logger.done()
        CONFIG.DEVICE.IS_PRODUCT_BUILD = False
        return True

    def remount(self, disable_verity=False, disable_wptest=False, timeout=DEFAULT_REMOUNT_TIMEOUT, **kwargs):
        """
        Remount partitions. Raises error when failed.

        Args:
            disable_verity (bool, default False): Disable verity with reboot device.
            disable_wptest (bool, default False): Disable wptest in fastboot. Works with old devices.
            timeout (int, default :data:`.constants.DEFAULT_REMOUNT_TIMEOUT`): Timeout in seconds

        Keyword args:
            verbose (bool, default :data:`.constants.DEFAULT_MANAGER_COMMAND_VERBOSE`): Print process to output

        Raises:
            RemountFailedError if remount not allowed
        """
        start_time = time()
        self.root(timeout=timeout, **kwargs)
        verbose = kwargs.get('verbose', DEFAULT_MANAGER_COMMAND_VERBOSE)

        timeout, start_time = self._reduce_timeout(start_time, timeout)
        out = self.adb('remount', timeout=timeout, **kwargs)

        if re.search('fastboot oem wptest disable', out, re.I):
            if disable_wptest is False:
                raise RemountFailedError('%s is required !' % NAME.safe_substitute(name='fastboot oem wptest disable'))
            else:
                timeout, start_time = self._reduce_timeout(start_time, timeout)
                self.reboot_to('fastboot', timeout=timeout, **kwargs)
                try:
                    if verbose:
                        self.logger.info('Disabling wptest...')
                    # disable wptest
                    timeout, start_time = self._reduce_timeout(start_time, timeout)
                    self.fb('oem wptest disable', timeout=timeout, **kwargs)
                    if verbose:
                        self.logger.done()
                finally:
                    # reboot
                    timeout, start_time = self._reduce_timeout(start_time, timeout)
                    self.reboot_to('adb', timeout=timeout, **kwargs)
        elif re.search('dm_verity is enabled|adb disable-verity', out, re.I):
            if disable_verity is False:
                raise RemountFailedError('%s is required !' % NAME.safe_substitute(name='adb disable-verity'))
            else:
                if verbose:
                    self.logger.info('Disabling dm_verity...')
                # disable verity
                timeout, start_time = self._reduce_timeout(start_time, timeout)
                self.adb('disable-verity', errors=True, timeout=timeout, **kwargs)
                # reboot
                timeout, start_time = self._reduce_timeout(start_time, timeout)
                self.reboot_to('adb', force=True, timeout=timeout, **kwargs)
                # root
                timeout, start_time = self._reduce_timeout(start_time, timeout)
                self.root(timeout=timeout, **kwargs)
                # remount
                timeout, start_time = self._reduce_timeout(start_time, timeout)
                out = self.adb('remount', errors=True, timeout=timeout, **kwargs)
                if verbose:
                    self.logger.done()
        if re.search('fail', out, re.I):
            raise RemountFailedError(out)

    def __push_pull_base(self, path, file, push=True, timeout=None, **kwargs):
        """
        Pull/push base function.

        Function tries request root permissions or remount if required.

        Args:
            path (str): Path to file or folder
            file (str): Path to file or folder
            push (bool): 'push' if True 'pull' otherwise
            timeout (int): Timeout in seconds

        Keyword args:
            verbose (bool, default :data:`.constants.DEFAULT_MANAGER_COMMAND_VERBOSE`): Print process to output
            allow_root (bool, default True): Allow to root access request if required
            allow_remount (bool, default True): Allow to remount request if required

        Todo:
            - Check file exists
            - fix folder to folder path with latest adb
        """
        start_time = time()
        first = kwargs.get('first_try', True)
        verbose = kwargs.get('verbose', DEFAULT_MANAGER_COMMAND_VERBOSE)
        allow_root = kwargs.get('allow_root', True)
        allow_remount = kwargs.get('allow_remount', True)
        try:
            if verbose:
                self.logger.info('%s [%s -> %s]' % ('Pushing' if push else 'Pulling', path, file))
            out = self.adb('%s %s %s' % ('push' if push else 'pull', path, file), timeout=timeout, **kwargs)
        except AccessDeniedError:
            if not first or not allow_root:
                raise
            # try to get root
            timeout, start_time = self._reduce_timeout(start_time, timeout)
            self.root(timeout=timeout, **kwargs)
            timeout, start_time = self._reduce_timeout(start_time, timeout)
            out = self.__push_pull_base(path=path, file=file, push=push, timeout=timeout, first_try=False)
        except ObjectDoesNotExistError:
            if not first or not allow_remount:
                raise
            # try to remount
            timeout, start_time = self._reduce_timeout(start_time, timeout)
            self.remount(timeout=timeout, **kwargs)
            timeout, start_time = self._reduce_timeout(start_time, timeout)
            out = self.__push_pull_base(path=path, file=file, push=push, timeout=timeout, first_try=False)
        else:
            if verbose:
                self.logger.done()
        return out

    def pull(self, path, file, timeout=DEFAULT_PULL_TIMEOUT, **kwargs):
        """
        Pull file or folder from device

        Args:
            path (str): Path to file or folder on device
            file (str): Path when file or folder should be saved
            timeout (int, default :data:`.constants.DEFAULT_PULL_TIMEOUT`): Timeout in seconds

        Keyword args:
            verbose (bool, default :data:`.constants.DEFAULT_MANAGER_COMMAND_VERBOSE`): Print process to output
            allow_root (bool, default True): Allow to root access request if required
            allow_remount (bool, default True): Allow to remount request if required
        """
        return self.__push_pull_base(path=path, file=file, push=False, timeout=timeout, **kwargs)

    def push(self, file, path, timeout=DEFAULT_PUSH_TIMEOUT, **kwargs):
        """
        Push file or folder to device

        Args:
            file (str): Path to file or folder
            path (str): Path on device when file or folder should be saved
            timeout (int, default :data:`.constants.DEFAULT_PUSH_TIMEOUT`): Timeout in seconds

        Keyword args:
            verbose (bool): Print process to output
            allow_root (bool, default True): Allow to root access request if required
            allow_remount (bool, default True): Allow to remount request if required

        Raises:
            ObjectDoesNotExistError when file or folder not found
        """
        if not os.path.exists(file):
            raise ObjectDoesNotExistError('%s file or folder not found !' % NAME.safe_substitute(name=file))

        return self.__push_pull_base(path=file, file=path, push=True, timeout=timeout, **kwargs)

    async def first_detect(self, timeout=DEFAULT_FIRST_DEVICE_DETECT_TIMEOUT, **kwargs) -> (str, str):
        """
        Async function of detect device first time and get device serial

        Args:
            timeout (int, default :data:`.constants.DEFAULT_FIRST_DEVICE_DETECT_TIMEOUT`): Timeout in seconds

        Keyword args:
            verbose (bool, default :data:`.constants.DEFAULT_MANAGER_COMMAND_VERBOSE`): Print process to output
            allow_adb_kill (bool, default :data:`.constants.DEFAULT_ADB_SERVER_KILL_ALLOWED`): Allow to kill ADB server

        Warning:
            allow_adb_kill == True may affect other script and not recommended to use except Framework was started
            isolated via Docker or Virtual Machine.

        Raises:
            TimeoutExpiredError when device not found and timeout expired
            DeviceEnumeratedError if found more one devices or device status is not good

        Returns:
            (str, str): Device serial and "adb" of "fastboot" mode
        """
        verbose = kwargs.get('verbose', DEFAULT_MANAGER_COMMAND_VERBOSE)
        allow_adb_kill = kwargs.get('allow_adb_kill', DEFAULT_ADB_SERVER_KILL_ALLOWED)

        if verbose:
            self.logger.info('Search for device in progress...')
        t = time()
        while (time() - t) <= timeout:
            a_devices, a_status = self.adb.devices(**kwargs)
            f_devices, f_status = self.fb.devices(**kwargs)
            # devices in adb and fastboot in same time
            if len(a_devices) > 0 and len(f_devices) > 0:
                raise DeviceEnumeratedError('More one device enumerated. Please provide serial number.')
            # one more device found
            elif len(a_devices) > 1 or len(f_devices) > 1:
                raise DeviceEnumeratedError('More one device enumerated. Please provide serial number.')
            # adb mode
            if len(a_devices) == 1:
                if a_status[0] == 'offline' and allow_adb_kill is True:
                    # restart adb server once
                    self.adb.restart_server(**kwargs)
                    allow_adb_kill = False
                elif a_status[0] == 'device':
                    if verbose:
                        self.logger.info('Detected device %s in ADB mode.'
                                         % (NAME.safe_substitute(name=a_devices[0])))
                    return a_devices[0], 'adb'
                else:
                    raise DeviceEnumeratedError('Device %s detected with status %s'
                                                % (NAME.safe_substitute(name=a_devices[0]),
                                                   NAME.safe_substitute(name=a_status[0])))
            # fastboot mode
            elif len(f_devices) == 1:
                if verbose:
                    self.logger.info('Detected device %s in FASTBOOT mode.' % (NAME.safe_substitute(name=f_devices[0])))
                return f_devices[0], 'fastboot'
            await asyncio.sleep(1)
        raise TimeoutExpiredError('Device not found !')

    def __check_mode(self, allow_adb_kill=DEFAULT_ADB_SERVER_KILL_ALLOWED, **kwargs):
        """
        Check device mode. Base function for :func:`get_mode` and :func:`find_device` functions

        Args:
            allow_adb_kill (bool, default :data:`.constants.DEFAULT_ADB_SERVER_KILL_ALLOWED`): Allow to kill ADB server

        Warning:
            allow_adb_kill == True may affect other script and not recommended to use except Framework was started
            isolated via Docker or Virtual Machine.

        Raises:
            TimeoutExpiredError when device not found and timeout expired
            DeviceEnumeratedError when device detected in wrong status

        Returns:
            tuple: (str: 'adb' or 'fastboot', bool: allow_adb_kill)
        """
        a_devices, a_status = self.adb.devices(**kwargs)
        if self.serial.upper() in a_devices:
            if a_status[a_devices.index(self.serial.upper())] == 'offline' and allow_adb_kill is True:
                # restart adb server once
                self.adb.restart_server(**kwargs)
                allow_adb_kill = False
            elif a_status[a_devices.index(self.serial.upper())] == 'device':
                return 'adb', allow_adb_kill
            else:
                raise DeviceEnumeratedError('Device %s was detected with %s status'
                                            % (NAME.safe_substitute(name=self.serial),
                                               NAME.safe_substitute(
                                                   name=a_status[a_devices.index(self.serial.upper())])))
        else:
            f_devices, f_status = self.fb.devices(**kwargs)
            if self.serial.upper() in f_devices:
                return 'fastboot', allow_adb_kill
        return None, allow_adb_kill

    async def async_get_mode(self, timeout=DEFAULT_WAIT_DEVICE_TIMEOUT, **kwargs) -> str:
        """ Async variant of :func:`get_mode` function """
        allow_adb_kill = kwargs.get('allow_adb_kill', DEFAULT_ADB_SERVER_KILL_ALLOWED)

        t = time()
        while (time() - t) <= timeout:
            mode, allow_adb_kill = self.__check_mode(allow_adb_kill, **kwargs)
            if mode is None:
                await asyncio.sleep(1)
            else:
                return mode
        raise TimeoutExpiredError('Device not found !')

    def get_mode(self, timeout=DEFAULT_WAIT_DEVICE_TIMEOUT, **kwargs) -> str:
        """
        Get device mode.

        Args:
            timeout (int, default :data:`.constants.DEFAULT_WAIT_DEVICE_TIMEOUT`): Timeout in seconds

        Keyword args:
            allow_adb_kill (bool, default :data:`.constants.DEFAULT_ADB_SERVER_KILL_ALLOWED`): Allow to kill ADB server

        Warning:
            allow_adb_kill == True may affect other script and not recommended to use except Framework was started
            isolated via Docker or Virtual Machine.

        Raises:
            TimeoutExpiredError when device not found and timeout expired
            DeviceEnumeratedError when device detected in wrong status

        Returns:
            str 'adb' or 'fastboot'
        """
        allow_adb_kill = kwargs.get('allow_adb_kill', DEFAULT_ADB_SERVER_KILL_ALLOWED)

        t = time()
        while (time() - t) <= timeout:
            mode, allow_adb_kill = self.__check_mode(allow_adb_kill, **kwargs)
            if mode is None:
                sleep(1)
            else:
                return mode
        raise TimeoutExpiredError('Device not found !')

    def reboot_to(self, mode, force=False, wait=True, timeout=DEFAULT_WAIT_DEVICE_TIMEOUT, **kwargs):
        """
        Rebooting device to ADB or fastboot depend of **mode** variable.

        Args:
            mode ('adb' or 'fastboot' or 'fb')
            force (bool, default False): Force reboot device whatever if device already in this mode
            wait (bool, default True): Waiting for device after reboot
            timeout (int, default :data:`.constants.DEFAULT_WAIT_DEVICE_TIMEOUT`): Timeout in seconds

        Keyword args:
            verbose (bool, default :data:`.constants.DEFAULT_MANAGER_COMMAND_VERBOSE`): Print process to output
        """
        # check mode variable
        req_mode = mode.lower().strip()
        if req_mode not in FASTBOOT_MODE_ALIASES and req_mode not in ADB_MODE_ALIASES:
            raise CommandExecuteError('%s device mode is not supported' % NAME.safe_substitute(name=req_mode).upper())

        start_time = time()
        verbose = kwargs.get('verbose', DEFAULT_MANAGER_COMMAND_VERBOSE)
        current_mode = self.get_mode(timeout=timeout, **kwargs)
        timeout, start_time = self._reduce_timeout(start_time, timeout)

        if current_mode != req_mode or force:
            # reset saved mode
            self.__update_saved_mode(None)
            if current_mode == 'adb':
                if req_mode in FASTBOOT_MODE_ALIASES:
                    if verbose:
                        self.logger.info('Rebooting device to FASTBOOT...')
                    self.adb.reboot_bootloader(**kwargs)
                    if verbose:
                        self.logger.done()
                else:
                    if verbose:
                        self.logger.info('Rebooting device to ADB (forcibly)...')
                    self.adb.reboot(**kwargs)
                    if verbose:
                        self.logger.done()
            else:
                if req_mode in ADB_MODE_ALIASES:
                    if verbose:
                        self.logger.info('Rebooting device to ADB...')
                    self.fastboot.reboot(**kwargs)
                    if verbose:
                        self.logger.done()
                else:
                    if verbose:
                        self.logger.info('Rebooting device to FASTBOOT (forcibly)...')
                    self.fastboot.reboot_bootloader(**kwargs)
                    if verbose:
                        self.logger.done()

        # wait for device
        if wait:
            timeout, start_time = self._reduce_timeout(start_time, timeout)
            self.wait_for(mode, timeout=timeout, **kwargs)

    def wait_for(self, mode, timeout=DEFAULT_WAIT_DEVICE_TIMEOUT, sleep_time=DEFAULT_SLEEP_FOR_WAIT_ADB, **kwargs):
        """
        Waiting for device loading in ADB or fastboot state depends of **mode** variable.

        Args:
            mode (str): Required mode to wait device
            timeout (int, default :data:`.constants.DEFAULT_WAIT_DEVICE_TIMEOUT`): Timeout in seconds
            sleep_time (int, default :data:`.constants.DEFAULT_SLEEP_FOR_WAIT_ADB`): Sleep time in second after device
                was detected in ADB

        Keyword args:
            allow_adb_kill (bool, default :data:`.constants.DEFAULT_ADB_SERVER_KILL_ALLOWED`): Allow to kill ADB server

        Warning:
            allow_adb_kill == True may affect other script and not recommended to use except Framework was started
            isolated via Docker or Virtual Machine.

        Raises:
            TimeoutExpiredError when device not found and timeout expired
            InconsistentStateError when device detected in wrong mode after timeout
        """
        # check mode variable
        req_mode = mode.lower().strip()
        if req_mode in ADB_MODE_ALIASES:
            req_mode = 'adb'
        elif req_mode in FASTBOOT_MODE_ALIASES:
            req_mode = 'fastboot'
        else:
            raise CommandExecuteError('%s device mode is not supported' % req_mode.upper())

        verbose = kwargs.get('verbose', DEFAULT_MANAGER_COMMAND_VERBOSE)
        # wait for device
        t = time()
        printed = False  # use for print message once
        current = None
        start_time = time()  # use to reduce timeout in each cycles
        mode_timeout = timeout
        while (time() - t) <= timeout:
            current = self.get_mode(timeout=mode_timeout, **kwargs)
            if current == req_mode:
                # sleep after detect device but only once
                if req_mode == 'adb' and current != self.saved_mode:
                    sleep(sleep_time)
                # update saved mode to skip sleep timeout next time
                self.__update_saved_mode(current)
                if verbose and printed:
                    self.logger.done()
                return
            # print message once if required
            elif not printed and verbose:
                printed = True
                self.logger.info('Waiting for device in %s mode...' % req_mode.upper())
            sleep(1)
            mode_timeout, start_time = self._reduce_timeout(start_time, timeout)

        if current is not None and current != req_mode:
            raise InconsistentStateError('Device found in %s mode, but excepted in %s mode'
                                         % (current.upper(), req_mode.upper()))
        raise TimeoutExpiredError('Device not found !')

    def wait_idle(self, timeout=DEFAULT_WAIT_DEVICE_TIMEOUT, sleep_time=DEFAULT_SLEEP_FOR_WAIT_IDLE,
                  windows_threshold=DEFAULT_WINDOWS_THRESHOLD_FOR_DETECT_IDLE, **kwargs):
        """
        Waiting for device loading to IDLE state (home or setup screen).

        Args:
            timeout (int, default :data:`.constants.DEFAULT_WAIT_DEVICE_TIMEOUT`): Timeout in seconds
            sleep_time (int, default :data:`.constants.DEFAULT_SLEEP_FOR_WAIT_IDLE`): Sleep time in seconds after
                Idle was detected.
            windows_threshold (int, default :data:`.constants.DEFAULT_WINDOWS_THRESHOLD_FOR_DETECT_IDLE`): Windows
                threshold to make sure Idle is detected

        Raises:
            TimeoutExpiredError
        """
        # wait device in ADB
        start_time = time()
        verbose = kwargs.get('verbose', DEFAULT_MANAGER_COMMAND_VERBOSE)
        kwargs['verbose'] = False
        self.wait_for('adb', timeout=timeout, **kwargs)
        timeout, start_time = self._reduce_timeout(start_time, timeout)

        printed = False  # used for print message once
        # wait for Idle
        t = time()
        shell_timeout = timeout
        while time() - t < timeout:
            find = re.findall('Window\s*([#\d]+)\s', self.sh('dumpsys window w | grep Window', errors=False, empty=True,
                                                             timeout=shell_timeout, **kwargs), re.I)
            self.syslogger.info('WAITIDLE Windows found: %d' % len(find))
            if len(find) >= windows_threshold:
                # sleep after Idle was detected but only once
                if self.saved_mode not in ['idle', 'service']:
                    # update saved mode to skip sleep timeout next time
                    self.__update_saved_mode('idle')
                    sleep(sleep_time)
                if verbose and printed:
                    self.logger.done()
                return
            else:
                if verbose and not printed:
                    printed = True
                    self.logger.info('Waiting for device in IDLE mode...')
                sleep(1)
            shell_timeout, start_time = self._reduce_timeout(start_time, timeout)
        raise TimeoutExpiredError('Wait for device in IDLE timeout expired !')

    def wait_service(self, service, timeout=DEFAULT_WAIT_SERVICE_TIMEOUT,
                     sleep_time=DEFAULT_SLEEP_FOR_WAIT_SERVICE, **kwargs):
        """
        Waiting for device service loading

        Args:
            service (str): Service to wait
            timeout (int, default :data:`.constants.DEFAULT_WAIT_SERVICE_TIMEOUT`): Timeout in seconds
            sleep_time (int, default :data:`.constants.DEFAULT_SLEEP_FOR_WAIT_SERVICE`): Sleep time in seconds after
                Idle was detected

        Raises:
            :class:`.exceptions.TimeoutExpiredError`
        """

        # wait device in ADB
        start_time = time()
        verbose = kwargs.get('verbose', DEFAULT_MANAGER_COMMAND_VERBOSE)
        kwargs['verbose'] = False
        self.wait_for('adb', timeout=timeout, **kwargs)
        timeout, start_time = self._reduce_timeout(start_time, timeout)

        printed = False  # used for print message once
        # wait for service
        t = time()
        shell_timeout = timeout
        while time()-t < timeout:
            out = self.sh('service check %s' % service, errors=False, empty=True, timeout=shell_timeout, **kwargs)
            if re.search('service\s+'+service+':\s+found', out, re.I):
                # sleep after Service was detected but only once
                if self.saved_mode != 'service':
                    # update saved mode to skip sleep timeout next time
                    self.__update_saved_mode('service')
                    sleep(sleep_time)
                if verbose and printed:
                    self.logger.done()
                return
            else:
                if verbose and not printed:
                    printed = True
                    self.logger.info('Waiting for [%s] service...' % service)
                sleep(1)
            shell_timeout, start_time = self._reduce_timeout(start_time, timeout)
        raise TimeoutExpiredError('Wait for service timeout expired !')
