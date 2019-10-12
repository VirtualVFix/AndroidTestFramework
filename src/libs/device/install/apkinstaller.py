# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Oct 12, 2016 12:12:00 PM$"

import re
import os
import hashlib
from config import CONFIG
from libs.cmd import Manager
from libs.core.logger import getLogger
from pkg_resources import parse_version
from libs.path import find_path_by_regexp
from libs.core.tools import NotImplemented
from .exceptions import InstallError, ApkNotFoundError
from libs.cmd.implement.exceptions import TimeoutExpiredError
from .constants import REMOVE_CONTENT_TIMEOUT, UNINSTALL_APP_TIMEOUT
from .constants import INSTALL_APP_TIMEOUT, INSTALL_PUSH_CONTENT_TIMEOUT, PHONE_TEMP_DIRECTORY


class ApkInstaller(Manager):
    def __init__(self, serial, logger=None):
        super(ApkInstaller, self).__init__(serial, logger=logger or getLogger(__file__))

    @NotImplemented
    def smartInstallApk(self, *a, **b):
        """ Smart install.  This function automatically press to 'accept' button on phone.
            This function must be replaced for used.
        """
    
    def getApkVersion(self, package):
        """ get apk version by package from shell """
        out = self.sh('dumpsys package %s | grep versionName' % (package), remove_line_symbols=True)\
            .replace('versionName=', '').strip()
        return out

    @staticmethod
    def getApkPath(apk_dir, apk_name, allowEnvironmentPath=True):
        """
        Find full path to application.

        Args:
            apk_dir (str): Path to folder with application
            apk_name (str): Apk name
            allowEnvironmentPath (bool): Allow to search by System environment variable
                configured in **CONFIG.SYSTEM.ENVIRONMENT_VARIABLE**
        """
        
        _path = find_path_by_regexp(default_dir=apk_dir, search_regexp=apk_name,
                                    allow_environment_path=allowEnvironmentPath)[0]
        if _path is None:
            raise ApkNotFoundError('Application [%s] not found !' % apk_name)
        return _path

    def installApk(self, apk_dir, apk_settings, allow_x64=False, smart_install=False, allowEnvironmentPath=True,
                   pushTimeout=None, installTimeout=None):
        """
        Install application to device.
        Function push application to temp folder on device and install it via *am* utility

        Args:
            apk_dir (str): Full to directory with application
            apk_settings (dict): Settings of application
            allow_x64 (bool): allow search x64 application in apk_path folder. x64 apk should ends with "_64bit.apk"
            smart_install (bool): Allow smart install with press "agree" messages and check pop up alerts
            allowEnvironmentPath (bool): Allow to search by System environment variable
                configured in **CONFIG.SYSTEM.ENVIRONMENT_VARIABLE**
            pushTimeout (int or None): Timeout in seconds to push application to device
            installTimeout (int or None): Install application timeout in seconds

        Note:
            **apk_settings** structure:

            .. code-block:: python

                apk_settings = {
                    'name': 'name',                 # name for logging
                    'apk'/'_apk':test.apk,          # apk file name  can be "_apk" settings to send as parameter
                    'package': 'package',           # apk package
                    'version':'1.0',                # apk version "dumpsys package PACKAGE| grep versionName"
                    'push': ('from', 'to')          # content for push to phone # should be in the same folder
                    'replace'/'_replace': False,    # allow replace application if it installed
                    'downgrade'/'_downgrade': True, # allow downgrade application version
                }
        """
        # keep_logger = self.logger
        assert isinstance(apk_settings, dict), '"apk_settings" value in "install()" function should be in dictionary !'
        assert ('apk' in apk_settings or '_apk' in apk_settings) and 'package' in apk_settings, \
            '"apk" or "package" value not found in "apk_settings" !'

        push = apk_settings['push'] if 'push' in apk_settings else None
        if push is not None:
            assert isinstance(push, tuple) or isinstance(push, list), \
                '"push" value in "apk_settings" variable should be in tuple or list !'
            
        replace = apk_settings['replace'] if 'replace' in apk_settings else apk_settings['_replace'] \
            if '_replace' in apk_settings else False
        downgrade = apk_settings['downgrade'] if 'downgrade' in apk_settings else apk_settings['_downgrade'] \
            if '_downgrade' in apk_settings else False
        version = apk_settings['version'] if 'version' in apk_settings else None
        log_name = apk_settings['name'] if 'name' in apk_settings else apk_settings['apk'][:-4]
        package = apk_settings['package']
        
        outp = ''
        apk = apk_settings['apk'] if 'apk' in apk_settings else apk_settings['_apk']
        # change apk to x64 if available
        if allow_x64:
            if CONFIG.DEVICE.CPU_64_BIT:
                apk64 = apk[:-4] + '_64bit.apk'
#                    if os.path.exists(apk_dir + apk64): 
                try:
                    self.getApkPath(apk_dir, apk64, allowEnvironmentPath)
                    apk = apk64
                    self.logger = getLogger(log_name + ' (x64)')
                except: pass
                
        # update keepd logger
        keep_logger = self.logger   
        try:
            self.logger = getLogger(log_name)
            # start installation
            self.syslogger.info('Start of installation procedure for [{}] application...'.format(log_name))
            # check if package are installed
            if not replace:
                self.syslogger.info('Checking for [{}] package...'.format(package))
                dumpsys_apk_version = self.getApkVersion(package)
                self.syslogger.info('Installed version: {} - Required: {} '.format(dumpsys_apk_version or 'none', version))
                if dumpsys_apk_version != '' and (version is not None and version == dumpsys_apk_version):
                    self.logger.info('Application is already installed.', self.syslogger)
                    outp = "Success"
                    return

            # check if application exists and keep path 
            application_path = self.getApkPath(apk_dir, apk, allowEnvironmentPath)
            self.syslogger.info('Application path: {}'.format(application_path))
            # push apk to temp folder if necessary
            self.syslogger.info('Pushing [{}] application to "{}" directory...'.format(apk, PHONE_TEMP_DIRECTORY))
            shell_md5 = ''
            apk_md5 = None
            out = self.sh('ls ' + PHONE_TEMP_DIRECTORY)
            if apk in out:
                try: # check md5sum
                    shell_md5 = self.sh('md5sum {}{}'.format(PHONE_TEMP_DIRECTORY, apk)).strip().split(' ')[0]
#                    with open(apk_dir+apk, 'rb') as file:
                    with open(application_path, 'rb') as file:
                        apk_md5 = hashlib.md5(file.read()).hexdigest()
                except Exception as e:
                    if CONFIG.SYSTEM.DEBUG:
                        self.logger.exception(e)
                    self.syslogger.error(e)
                self.syslogger.info('shell md5sum: {} - apk md5sum: {}'.format(shell_md5, apk_md5))
            # push apk if md5 not equals
            if shell_md5 != apk_md5:
                self.logger.info('Pushing [{}] application to "{}" directory...'.format(apk, PHONE_TEMP_DIRECTORY))
                self.push(application_path, PHONE_TEMP_DIRECTORY, timeout=installTimeout or INSTALL_APP_TIMEOUT)
                self.logger.done()

            # smark install 
            if smart_install:
                self.logger.info('Installing [{}] application with smart install...'.format(apk))
                outp = self.smartInstallApk({'_apk': apk, '_replace': replace, '_downgrade':downgrade})
            else: # regular install application
                self.logger.info('Installing [{}] application...'.format(apk))
                outp = self.sh('pm install -t ' + (' -r ' if replace else '') + (' -d ' if downgrade else '') 
                               + PHONE_TEMP_DIRECTORY + apk, errors=False,
                               timeout=installTimeout or INSTALL_APP_TIMEOUT)
#                self.logger.done()
            self.syslogger.info(outp)
        except Exception as e:
            self.syslogger.exception(e)
            if CONFIG.SYSTEM.DEBUG:
                self.logger.exception(e)
            raise
        else:
            # push apk content if available
            if "Success" in outp or 'INSTALL_FAILED_ALREADY_EXISTS' in outp or outp == '':
                self.logger.done()
                if push is not None:
                    _push_list = push if isinstance(push, list) else [push]
                    for _pname, _ppath in _push_list:
                        self.logger.info('Pushing application content [{}] to [{}]'.format(_pname, _ppath))
                        content = self.getApkPath(apk_dir, _pname, allowEnvironmentPath)
                        
                        # ----------------------- fix push directory on ADB 1.0.36+ version ----------------------------
                        if os.path.isdir(content) and _ppath.endswith('/'):
                            # get adb version
                            adb_ver = self.adb.version()
                            if adb_ver > parse_version('1.0.36'):
                                self.syslogger.info('Fix folder push for ADB "%s" version !' % adb_ver.base_version)
                                _ppath = os.path.split(_ppath[:-1])[0]
                        # ----------------------------------- end of ADB push fix --------------------------------------
                        
                        # push content        
                        self.push(content, _ppath, timeout=pushTimeout or INSTALL_PUSH_CONTENT_TIMEOUT)
                        self.logger.done()
                try: # save installed apk version
                    ver = self.getApkVersion(package)
                    if ver != '' and ver != 'null':
                        apk_settings['version'] = ver
                except Exception as e:
                    self.syslogger.exception(e)
                    if CONFIG.SYSTEM.DEBUG:
                        self.logger.exception(e)
            else: 
                # raise exception for exists reasons
                for x in ['INSTALL_FAILED_TEST_ONLY',
                          'INSTALL_FAILED_VERIFICATION_TIMEOUT', 
                          'INSTALL_FAILED_INVALID_URI', 
                          'INSTALL_FAILED_VERSION_DOWNGRADE', 
                          'INSTALL_FAILED_NO_MATCHING_ABIS',
                          'INSTALL_FAILED_UPDATE_INCOMPATIBLE',
                          'INSTALL_PARSE_FAILED_INCONSISTENT_CERTIFICATES']:
                    if x in outp:
                        _msg = apk + " installation failed: " + re.sub('[\t\r\n]+', ' ', x)
                        self.logger.error(_msg)
                        raise InstallError(_msg)
                raise InstallError(apk + " installation failed: " + outp)
        finally:
            self.logger = keep_logger # return logger
            try: # remove pushed apk
                if not CONFIG.SYSTEM.DEBUG:
                    out = self.sh('rm ' + PHONE_TEMP_DIRECTORY + apk)
                    self.syslogger.info(out)
            except Exception as e:
                self.syslogger.error(e)
        
    def uninstallApk(self, apk_settings):
        """ Uninstall application """
        assert isinstance(apk_settings, dict), '"apk_settings" value in "install()" function should be in dictionary !'
        assert 'package' in apk_settings, '"package" value not found in "apk_settings" !'
        package = apk_settings['package']
        log_name = apk_settings['name'] if 'name' in apk_settings else apk_settings['apk'][:-4]
        push = apk_settings['push'] if 'push' in apk_settings else None
        if push is not None:
            assert isinstance(push, tuple) or isinstance(push, list), '"push" value in "apk_settings" variable should be in tuple or list !'
        try:
            # uninstall
            self.logger.info('Uninstalling [{}] package...'.format(package))
            outp = self.sh("pm uninstall " + package, timeout = UNINSTALL_APP_TIMEOUT)
            if outp.startswith('Failure'): 
                self.logger.error('Uninstalling [{}] package failure'.format(package))
            self.logger.done()
            # check pushed content
            if push is not None: 
                _push_list = push if isinstance(push, list) else [push]
                for _pname, _ppath in _push_list:
                    self.removeContent(_ppath)
        except TimeoutExpiredError:
            msg = '{}: package [{}]: uninstall failed: Timeout expired.'.format(log_name, package)
            self.syslogger.exception(msg)
            if CONFIG.SYSTEM.DEBUG:
                raise Exception(msg)
            self.logger.error(msg + ' You can find details in sys.log.')
        except Exception as e:
            self.syslogger.exception('{}: uninstall error: {}'.format(log_name, e))
            if CONFIG.SYSTEM.DEBUG:
                raise Exception(self.syslogger.lastmessage())
            self.logger.warnlist(self.syslogger.lastmessage().replace('\n',''))
        
    def removeContent(self, path):
        """ Remove application content if available """
        try:
            # Check if folder exists. Error will be raised if not
            self.sh('ls ' + path, empty=True, errors=True)
        except: 
            pass
        else:
            self.logger.info('Removing application content: [{}]...'.format(path))
            self.sh('rm -r ' + path, timeout=REMOVE_CONTENT_TIMEOUT, empty=True)
            self.logger.done()
