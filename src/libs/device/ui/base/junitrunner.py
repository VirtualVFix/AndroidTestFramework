# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Oct 11, 2016 4:10:00 PM$"

import os
import re
import platform
import subprocess
from config import CONFIG
from libs.core.logger import getLogger
from libs.device.install import ApkInstaller
from .constants import APKS_DIR, PRINT_INFO_VALUES, PRINT_WARN_VALUES
from .constants import INSTALL_TEST_APP_TIMEOUT, SUBRESULTS_KEY_WORDS
from libs.device.ui.base.exceptions import JUnitRunnerError, ConsentDialogError
from .constants import DEFAULT_BASE_APK, DEFAULT_TEST_APK, LOG_FILE_NAME, ERROR_OUTPUT_LENGTH


class JUnitRunner(ApkInstaller):
    def __init__(self, serial, logger=None):
        super(JUnitRunner, self).__init__(serial, logger=logger or getLogger(__file__))
        self.uilogger = getLogger(__file__, LOG_FILE_NAME, propagate=False)
        if not hasattr(CONFIG.DEVICE, '_isjunitrunnerinstalled_'):
            CONFIG.DEVICE._isjunitrunnerinstalled_ = False

        self.summary_results = ''
        self.err = ''
        self.error = False
        
    def __parseOutput(self, text):
        self.uilogger.info(text)
        if not self.error and 'Exception' in text:
            self.error = True
        if not self.error: 
            if text.startswith(PRINT_INFO_VALUES):
                out = text.replace(PRINT_INFO_VALUES, '')
                if out.startswith('#RESULTS#'): 
                    self.summary_results = re.search('#RESULTS#(.*?)#ENDRESULTS#', text, re.I).group(1)
                    return
                if out.startswith(PRINT_WARN_VALUES):
                    self.logger.warnlist(out)
                else:
                    self.logger.info(out)
        elif not text.startswith('INSTRUMENTATION'):
            self.err += text + '\n'
    
    def __replaceSpecialSymbols(self, text):
        res = ''
        for x in text:
            if not re.search('[\w\d\[\]\s\-_\\\:,.+=@#;!?*"\'/]', x, re.I):
                _hex = x.encode('hex')
                res += '\\u' + '0'*(4-len(str(_hex))) + _hex
            else:
                res += x
        return res
    
    def __getSubResults(self, out):
        """ Pull screenshot or uidump if available in results """
        res = out 
        match = re.search('#(%s)#'%'|'.join(SUBRESULTS_KEY_WORDS), out, re.I)
        if not match: 
            return res
        sub = match.group(1)
        # split sub results
        for x in (y.strip() for y in res[res.find(sub)+len(sub)+1:].split(';') if y.strip() != ''):
            save_path = CONFIG.SYSTEM.LOG_PATH + '%s_%s_%s_%s_%s.%s'%(os.path.split(x)[1][:-4],
                                                                      CONFIG.DEVICE.CURRENT_STATE.replace(' ', '_'),
                                                                      CONFIG.DEVICE.CURRENT_SUITE,
                                                                      CONFIG.DEVICE.CURRENT_CYCLE,
                                                                      CONFIG.DEVICE.LOCAL_CURRENT_CYCLE,
                                                                      x[-3:])
            # rename file if exists
            for i in range(1, 1000, 1):
                if os.path.exists(save_path):
                    save_path = save_path[:-4 if i==1 else -6-len(str(i))] + '_r%d.%s'%(i, x[-3:])
                else: 
                    break    
            # pull files
            self.pull(x, save_path, timeout=120)
            self.logger.info('%s saved in "%s"'%(sub.capitalize(), save_path))
            
        return res[:res.find(sub)-1]        
    
    def __generateJUnitCommandLine(self, arguments, package, clazz, function=None):
        """
        Generate command for launch test like:
        **adb shell am instrument -w -r   -e debug false -e class kernel.bsp.test.ui.benchmarks.tests.Smartbench
        kernel.bsp.test.ui.benchmarks.test/android.support.test.runner.AndroidJUnitRunner**

        Args:
            arguments (dict): {value:'skip', _value:'send'} Application settings dictionary.
                Values with "_" will be added to launch command line as parameters
            package (str): Full name of test package
            clazz (str): Tull name of test class in test apk
            function (str) Test function from test class if required

        """
        assert isinstance(arguments, dict), '"Arguments" values in "__generateJUnitCommandLine()" ' \
                                            'function should be in dictionary !'
        cmd = 'adb -s %s shell am instrument -w -r   -e debug false -e class %s%s' \
              % (self.serial, clazz, ('#'+function) if function is not None else '')
        
        for x in arguments.keys():
            if x.startswith('_'):
                cmd += ' -e ' + x[1:] + ' "'
                cmd += self.__replaceSpecialSymbols(re.sub('[\(\)\[\]\'\s]+', '',
                                                           str(self.getValueForCurrentDevice(arguments[x]))))
                cmd += '"'
        return cmd + ' ' + package + '/android.support.test.runner.AndroidJUnitRunner'
    
    def __run(self, command):
        self.uilogger.info(command)
        process = subprocess.Popen(command, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   shell=False if platform.system().lower() == 'windows' else True)
        while True:
            raw = process.stdout.readline()
            # EOF
            if not raw:
                break

            # ignore read errors
            line = raw.decode(encoding='utf-8', errors='replace').rstrip()
            self.__parseOutput(line.rstrip())
            if process.stderr:
                raise JUnitRunnerError(process.stderr)
        process.wait()
        if self.error:
            self.__getSubResults(self.summary_results)
            if CONFIG.SYSTEM.DEBUG:
                # cut error due to it's really long
                err = self.err
                if ERROR_OUTPUT_LENGTH > 0:
                    tm = self.err.split('\n')
                    if len(tm) > ERROR_OUTPUT_LENGTH: 
                        err = '\n'.join([tm[i] for i in range(ERROR_OUTPUT_LENGTH)]) \
                              + '... You can find details in "{}" file.'.format(LOG_FILE_NAME)
                raise JUnitRunnerError(err)
            else:
                raise JUnitRunnerError(self.err.split('\n')[0]
                                       + '... You can find details in "{}" file.'.format(LOG_FILE_NAME))
    
    def getValueForCurrentDevice(self, data):
        """ get value from dictionary data by device type """
        if isinstance(data, dict):
            if CONFIG.DEVICE.DEVICE_NAME in data.keys():
                return data[CONFIG.DEVICE.DEVICE_NAME]
            if CONFIG.DEVICE.DEVICE_NAME.split('_')[0] + '*' in data.keys():
                return data[CONFIG.DEVICE.DEVICE_NAME.split('_')[0] + '*']
            return data['all']
        else: return data

    def installJUnitTestsLauncher(self, apk_dir=None, base_settings=None, test_settings=None):
        """
        Install base and test package

        Args:
            apk_dir (str): Full path to directory with JUnit Base and Test apk
            base_settings (dict): Install settings of JUnit Base apk.
                Detailed settings structure described in :func:`.install.apkinstaller.ApkInstaller.installApk` function.
            test_settings (dict): Install settings of JUnit Test apk.
                Detailed settings structure described in :func:`.install.apkinstaller.ApkInstaller.installApk` function.

        Note:
            apk_dir, base_settings, test_settings parameters will be used from default config if those options == None
        """
        if not CONFIG.DEVICE._isjunitrunnerinstalled_:
            directory = apk_dir or APKS_DIR
            base = base_settings or DEFAULT_BASE_APK
            test = test_settings or DEFAULT_TEST_APK
            
            # press consentDialog if exists
            def isConsentDialogDisplayed():
                if 'consentdialog' in str(self.sh('dumpsys window windows | grep -E mCurrentFocus',
                                                  errors=False, empty=True)).lower():
                    self.sh('input keyevent KEYCODE_DPAD_RIGHT && sleep 0.5 && input keyevent KEYCODE_ENTER',
                            errors=False, empty=True)
                    return True
                return False

            # base apk
    #        self.logger.info('Installation of Base application...')
            # try to install apk twice it required if consent dialog is present
            for x in range(2):
                try:
                    if x > 0:
                        self.syslogger('Base apk install retrying...')
                    self.installApk(directory, base, installTimeout=INSTALL_TEST_APP_TIMEOUT)
                except Exception as e:
                    if not isConsentDialogDisplayed: 
                        raise ConsentDialogError(e)
                else:
                    break
            # test apk
    #        self.logger.info('Installation of Test application...')
            # try to install apk twice it required if consent dialog is present
            for x in range(2):
                try:
                    if x > 0:
                        self.syslogger('Test apk install retrying...')
                    self.installApk(directory, test, installTimeout=INSTALL_TEST_APP_TIMEOUT)
                except Exception as e:
                    if not isConsentDialogDisplayed: 
                        raise ConsentDialogError(e)
                else:
                    break
            CONFIG.DEVICE._isjunitrunnerinstalled_ = True
        
    def uninstallJUnitTestsLauncher(self, base_settings=None, test_settings=None):
        """ uninstall base and test JUnit apks 
            base_package, test_package parameters will be used from default config if those options == None
        """
        base = base_settings or DEFAULT_BASE_APK
        test = test_settings or DEFAULT_TEST_APK
        
        # remove test 
#        self.logger.info('Uninstalling of Test application...')
        self.uninstallApk(test)
        # remove base
#        self.logger.info('Uninstalling of Base application...')
        self.uninstallApk(base)
        
        CONFIG.DEVICE._isjunitrunnerinstalled_ = False
    
    def forceStopJUnitTestsLauncher(self, package=None):
        pkg = package or DEFAULT_TEST_APK['package']        
        self.sh('am force-stop ' + pkg)
        pkg = package or DEFAULT_BASE_APK['package']
        self.sh('am force-stop ' + pkg)
        
    def smartInstallApk(self, apk_settings, test_class=None, test_package=None, install_function='install'):
        """
        Application smart install.
        This function automatically press to 'accept' button on phone.

        Args:
            apk_settings (dict): Test application settings.
                Detailed settings structure described in :func:`.install.apkinstaller.ApkInstaller.installApk` function.
            test_class (str):  Full name of test class
            test_package (str): Full name of test package
            install_function (str): Install function name in test apk
        """ 
        # install default test class if test_package and test_class is None
        if test_package is None and test_class is None:
            self.installJUnitTestsLauncher()
        self.launchJUnitTest(apk_settings, clazz=test_class or 'kernel.bsp.test.ui.benchmarks.support.Install',
                             package=test_package, function=install_function)
        return self.summary_results
    
    def launchJUnitTest(self, arguments, clazz, package=None, function=None):
        """ Launch AndroidJUnit test 
            package - full test package
            clazz - full name of test class
            function - function name if required
        """
        try:
            self.err = ''
            self.error = False
            self.summary_results = ''
#            self.logger.info('Running of AndroidJUnitRunner...')
            self.forceStopJUnitTestsLauncher()
            pkj = package or DEFAULT_TEST_APK['package']
            self.__run(self.__generateJUnitCommandLine(arguments, pkj, clazz, function))
        except Exception as e:
            self.syslogger.exception(e)
            raise JUnitRunnerError(e)
        finally:
            self.forceStopJUnitTestsLauncher()
            
    def getResults(self):
        """ get results from uiautomator """
        res = self.summary_results
        return self.__getSubResults(res)
