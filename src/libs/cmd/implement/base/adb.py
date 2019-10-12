# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "09/22/17 14:26"

import re
from .cmd import Cmd
from libs.core.template import NAME
from ..gurads import BaseGuard, AdbGuard
from libs.cmd.interface.adb import Adb as AdbInt
from ..constants import DEFAULT_MANAGER_COMMAND_VERBOSE


class Adb(Cmd, AdbInt):
    """
    ADB implementation based on system ADB bridge working via terminal.
    """

    def __init__(self, serial=None, logger=None, **kwargs):
        """
        Args:
            logger (logging): Custom logger if need output with one logger. New logger will be created if None. (Default: None)
            serial (str): Serial number of device. May be None (Default: None)
        """
        super(Adb, self).__init__(logger=logger, serial=serial, **kwargs)

    @AdbGuard
    @BaseGuard
    def __call__(self, command, barecmd=False, **kwargs):
        """
        Execute any ``adb`` command.

        Args:
            command (str): Str command to execute (without **adb -s SERIAL**)
            barecmd (bool): Execute ADB command with out serial number included

        Keyword args:
            timeout (int, optional): Command timeout
            error (bool, optional): Check errors in command output
            empty (bool, optional): Check if command output is empty
            retry_count = (int, default :data:`implements.constants.CMD_RETRY_COUNT`. Configured in **CMD_RETRY_COUNT**):
                Command retry counter. Allow retry when > 0
            switch_reconnect_after (int, default :data:`implements.constants.CMD_SWITCH_RECONNECT_AFTER`. Configured in
                **CMD_SWITCH_RECONNECT_AFTER**): Switch board reconnect after each N retry. Allow switch reconnect when
                > 0. Should be <= CMD_RETRY_COUNT
            allow_timeout_retry (bool, default :data:`implements.constants.CMD_RETRY_AFTER_TIMEOUT_ERROR`. Configured in
                **CMD_RETRY_AFTER_TIMEOUT_ERROR**): Allow retry after TimeoutExpired error
            switch_reconnect_delay (int, default :data:`implements.constants.CMD_SWITCH_RECONNECT_DELAY`. Configured in
                **CMD_SWITCH_RECONNECT_DELAY**): Switch reconnect delay in seconds
            retry_delay (int, default :data:`implements.constants.CMD_RETRY_DELAY`. Configured in **CMD_RETRY_DELAY**):
                Retry delay in seconds

        Returns:
             str: output or ''
        """
        kwargs = self.update_base_kwargs(**kwargs)
        cmd = ('adb -s %s %s' % (self.serial, command)) \
            if self.serial is not None and not barecmd else ('adb %s' % command)
        return super(Adb, self).__call__(cmd, **kwargs)

    def kill_server(self, **kwargs):
        """
        Killing ADB server.

        Warning:
            Killing ADB server may affect other script and not recommended to use except Framework was started
            isolated via Docker or Virtual Machine.
        """
        self.syslogger.warning('Killing ADB server...')
        self.__call__('kill-server', barecmd=True, **kwargs)
        self.syslogger.done()

    def start_server(self, **kwargs):
        """
        Start ADB server.
        """
        self.syslogger.warning('Starting ADB server...')
        self.__call__('start-server', barecmd=True, **kwargs)
        self.syslogger.done()

    def restart_server(self, **kwargs):
        """
        Restart ADB server.
        """
        verbose = kwargs.get('verbose', DEFAULT_MANAGER_COMMAND_VERBOSE)
        if verbose:
            self.logger.info('Trying to restart ADB server...')
        self.kill_server(**kwargs)
        self.start_server(**kwargs)
        if verbose:
            self.logger.done()

    def version(self, **kwargs):
        """
        Get ADB version

        Returns:
            ADB version as :func:`pkg_resources.parse_version`
        """
        from pkg_resources import parse_version
        try:
            out = self.__call__('version', **kwargs)
            match = re.search('version\s+([\d.]+)[\r\t\n]+', out, re.I)
            if match:
                return parse_version(match.group(1))
        except Exception as e:
            self.syslogger.exception(e)
        return parse_version('')

    def devices(self, **kwargs) -> tuple:
        """
        Get adb devices

        Returns:
            ([barcode], [status]): list of barcodes with list of statuses
        """
        out = self.__call__('devices', barecmd=True, **kwargs)
        dev = re.findall('([\d\w]+)\t([\w]+)', out, re.I)
        return [x[0].upper() for x in dev], [x[1].lower() for x in dev]

    def reboot(self, **kwargs):
        """
        Reboot device
        """
        self._current_mode = None
        self.__call__('reboot', **kwargs)

    def reboot_bootloader(self, **kwargs):
        """
        Reboot device to bootloader
        """
        self._current_mode = None
        self.__call__('reboot bootloader', **kwargs)

    def reboot_bl(self, **kwargs):
        """
        Reboot device to bootloader
        """
        return self.reboot_bootloader(**kwargs)

    def root(self, **kwargs) -> bool:
        """
        Request root permissions
        """
        raise NotImplementedError('%s function implemented in %s class !'
                                  % (NAME.safe_substitute(name='root'), NAME.safe_substitute(name='Manager')))

    def remount(self, **kwargs) -> bool:
        """
        Remount partitions
        """
        raise NotImplementedError('%s function implemented in %s class !'
                                  % (NAME.safe_substitute(name='remount'), NAME.safe_substitute(name='Manager')))

    def pull(self, path, file, **kwargs) -> bool:
        """
        Pull file or folder from device

        Args:
            path (str): Path to file or folder on device
            file (str): Path when file or folder should be saved

        Kwargs:
            timeout (int): Timeout in seconds
        """
        raise NotImplementedError('%s function implemented in %s class !'
                                  % (NAME.safe_substitute(name='pull'), NAME.safe_substitute(name='Manager')))

    def push(self, file, path, **kwargs) -> bool:
        """
        Push file or folder to device

        Args:
            file (str): Path to file or folder
            path (str): Path on device when file or folder should be saved

        Kwargs:
            timeout (int): Timeout in seconds
        """
        raise NotImplementedError('%s function implemented in %s class !'
                                  % (NAME.safe_substitute(name='push'), NAME.safe_substitute(name='Manager')))
