# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__="VirtualV <https://github.com/virtualvfix>"
__date__ = "$Aug 11, 2017 12:20:00 PM$"

import re
import os
import shutil
import platform
from config import CONFIG
from libs.device.shell import Base
from libs.core.logger import getLogger
from .localstorage import LocalStorage
from libs.build.base.exceptions import FlashError, BuildNotFoundError
from libs.build.base.config import DEFAULT_FLASH_TIMEOUT, DEFAULT_WAIT_TIMEOUT
from libs.build.base.config import BUILD_SERVER, BUILD_SERVER_NAME, BUILD_SERVER_PASSWORD, MINIMAL_FLASH_OPERATIONS
from libs.build.base.config import FILE_TO_FLASH_WINDOWS, FILE_TO_FLASH_LINUX, RE_PATTERN_COMPARE_BUILDS, MINIMAL_FLASH_TIME


class Flash(Base):
    def __init__(self, serial, logger=None):
        super(Flash, self).__init__(serial, logger or getLogger(__file__))

    def isFlashedBy(self, artifactname) -> bool:
        """
        Function to check - is it flashed by an artifactname (build) or not

        Args:
            artifactname (str): Name of an artifact (build) to compare

        Returns:
            True or False (successfulness of the comparison)
        """
        result = False
        
        # get device property
        self.prop.update_cache()
        buildinfo = self.prop.getBuildFingerprint().lower()
        if buildinfo == '':
            self.logger.error('Build fingerprint cannnot be got !')
            return False
        
        self.logger.info('Compare "%s" and "%s"'%(buildinfo, artifactname.lower()))
        try:
            m = re.match(RE_PATTERN_COMPARE_BUILDS, buildinfo)
            if m == None: 
                raise Exception('"%s" does not match "%s" pattern'%(buildinfo, RE_PATTERN_COMPARE_BUILDS))
        
            for g in m.groups():
                if artifactname.lower().count(g) == 0 and artifactname.lower().count(g.split('_')[0]) == 0:
                    self.logger.info('There is no "%s" in "%s"'%(g, artifactname.lower()))
                    break
            else: 
                result = True
        except Exception as e:
            raise
        
        self.logger.info("Comparison result: %s"%('PASS' if result else 'FAIL'))
        self.logger.newline()
        
        return result
    
    def _flashtime(self, text):
        """
        Return flash time by output
        """
        res = re.findall('time:\s([.\d]*)s', text, re.I)
        _sum = 0
        for x in res:
            _sum += float(x)
        if _sum < MINIMAL_FLASH_TIME:
            raise FlashError('Flash time less %d seconds. Out: %s' % (MINIMAL_FLASH_TIME, text))
        return _sum
    
    def _checkFlashLog(self, flashlog):
        """
        Check all parts of flash ware flashed successfully
        """
        msg = ' You can see details in sys.log'
        command = None
        part = None
        counter = 0
        self.logger.info('Checking flash log...')
        self.logger.table('-*')
        for line in flashlog.split('\n'):
            match = re.search('%s\s(flash|erase)([\w\d\s_.-]+)'%self.serial, line, re.I)
            if match:
                if part is not None:
                    raise FlashError('"%s" command failed !%s'%(command, msg))
                command = ''.join(match.groups())
                counter += 1
                part = None
                continue
                
            if command is not None:
                match = re.search('^(sending|erasing|writing)([\w\d\s\'"/_.-]+)', line, re.I)
                if match:
                    part = ''.join(match.groups()).replace('...','')
                    continue                

                if line.lower().startswith('okay'):
                    if part is None and 'reboot' not in command:
                        self.logger.table(('"%s" - "%s"' % (command, part), 90, 'L'), ('FAIL', 10, 'C'))
                        raise FlashError('"%s" command failed !%s' % (command, msg))
                    self.logger.table(('"%s" - "%s"' % (command, part), 90, 'L'), ('OKAY', 10, 'C'))
                    part = None
                    continue
                
                if line.lower().startswith('finish'):
                    command = None
        self.logger.table(('-*', 100))
        
        self.logger.info('Successful operations: %d'%counter)
        if counter < MINIMAL_FLASH_OPERATIONS:
            raise FlashError('To low flash operations in flash log !%s' % msg)
        self.logger.done()
    
    def flash(self, localpath, artifactname, erase=False, waitidle=True, checkerrors=True,
                    flashtimeout=DEFAULT_FLASH_TIMEOUT, waittimeout=DEFAULT_WAIT_TIMEOUT):
        """
        Flash device

        Args:
            localpath (str): Full path to local storage with build if exists
            artifactname (str): Artifactory name to check build on Actifactory server
            erase (bool, default False): Erase device before flash
            waitidle (bool, default True): Wait for device in Idle after flash
            checkerrors (bool, default True): Check errors during flash
            flashtimeout (int, default :data:`.base.config.DEFAULT_FLASH_TIMEOUT`): Flash timeout in seconds
            waittimeout (int, default :data:'.base.config.DEFAULT_WAIT_TIMEOUT'): Wait for device in Idle timeout
                in seconds

        Returns:
            str: Flash script output
        """
        self.logger.newline()
        self.logger.info('Build path: "%s"'%os.path.join(localpath, artifactname), self.syslogger)
        self.logger.newline(self.syslogger)
        self.logger.waring('(\|)^_^(\/) BUILD [%s] WILL BE USED FOR FLASHING DEVICE ! (\/)^_^(|/)'
                           % artifactname.upper(), self.syslogger)
        self.logger.newline(self.syslogger)
        
        self.logger.info('Wait for device in FASTBOOT mode...')
        self.reboot_to('fastboot', timeout=120)
        if erase:
            self.logger.info('Erasing user data and cache...')
            self.fastboot('erase userdata')
            self.fastboot('erase cache')
            self.reboot_to('fastboot', force=True, timeout=120)

        self.logger.newline()
        self.logger.warning('Device flashing in progress... Please don\'t interrup process.')
        self.logger.newline()
        
        # flash command
        if platform.system().lower() == 'windows':
            drive, path = os.path.splitdrive(localpath)
            cmd = 'cd ' + os.path.join(localpath, artifactname) + ' && ' + drive + ' && echo yes | ' \
                  + FILE_TO_FLASH_WINDOWS + ' /d ' + self.serial
        else:
            self.cmd('chmod -R 755 ' + os.path.join(localpath, artifactname), empty=True, errors=False, timeout=10)
            cmd = 'cd ' + os.path.join(localpath, artifactname) + '/&& yes | ./' + FILE_TO_FLASH_LINUX + ' ' \
                  + self.serial
        out = re.sub('[\t\r]+', '', self.cmd(cmd, errors=False, empty=False, timeout=flashtimeout).replace('\n\n','\n'))

        for x in out.split('\n'): 
            self.syslogger.info(x)
            
        if checkerrors:
            self._checkFlashLog(out)
        _time = self._flashtime(out)
        self.logger.info('Device flashing has been completed. Total time: %s sec. ' % _time
                         + 'You can see details in "sys.log" file in logs directory.')
        self.syslogger.info('Device flashing has been completed. Total time: %s sec.' % _time)
        self.logger.newline()
        
        if waitidle:
            self.logger.info('Wait for device in IDLE...')
            self.wait_idle(timeout=waittimeout)
            self.logger.info('Done.')
        else:
            self.logger.info('Wait for device in ADB...')
            self.reboot_to('adb', timeout=waittimeout)
            self.logger.info('Done.')

        if not self.isFlashedBy(artifactname):
            raise FlashError('Flashed build is not compared with device build !')
        self.logger.info('Device was flashed successfully !')
        return out
    
    def findBuildAndflash(self, localpath=None, jobname=None, buildtag=None, newbuild=False, erase=False, waitidle=True,
                          factory=False, rmdir=False, checkerrors=True, force=False,
                          flashtimeout=DEFAULT_FLASH_TIMEOUT, waittimeout=DEFAULT_WAIT_TIMEOUT):
        """
        Flash device with check and download build if required.

        Arguments:
            localpath (str, default None): Path to build. As path will be used **CONFIG.TEST.BUILD_PATH**
                or **CONFIG.SYSTEM.BUILD_FOLDER** if None
            jobname (str, default None): Jenkins build Job name. Build will not downloaded if None
            buildtag (str default None): Build tag like: nash_oem...
            newbuild (bool, default False): Raise exception if no new build found
            erase (bool, default False): Erase userdata and cache before flash
            waitidle (bool, default True): Wait for device in IDLE after flash
            factory (bool, default False): Add factory prefix to buildtag
            rmdir (bool, default False): Remove build folder after flash
            checkerrors (bool, default True): Check errors for all write/erase operations in flash log
            force (bool, default False): Force flash build even if latest good build already flashed
            flashtimeout (int, default :data:`.base.config.DEFAULT_FLASH_TIMEOUT`) Flash timeout in seconds
            waittimeout (int, default :data:`.base.config.DEFAULT_WAIT_TIMEOUT`) Wait for device in Idle timeout
                in seconds

        Returns:
            str: Path to found build and artifact name or raise exception if something wrong
        """
        flashednew = False # is new build flashed
        buildpath, artifactname = None, None
        try:
            localstorage = LocalStorage(localpath)
            # flash local storage build
            if jobname is None:
                buildpath, artifactname = localstorage.getLocalStorageBuild(buildtag=buildtag, factory=factory)
                flashedby = self.isFlashedBy(artifactname)
                if not flashedby or force:
                    if not (flashedby & newbuild):
                        self.flash(localpath=buildpath, artifactname=artifactname, erase=erase,
                                   waitidle=waitidle, checkerrors=checkerrors, 
                                   flashtimeout=flashtimeout, waittimeout=waittimeout)
                        flashednew = True
                else:
                    self.logger.warn('Latest build already flashed on device !')
            else: # check artifactory build
                from .buildserver import BuildServer
                buildserver = BuildServer(BUILD_SERVER, BUILD_SERVER_NAME, BUILD_SERVER_PASSWORD) 
                allartifacts, artifactname = buildserver.check_latest_good_build(jobname, buildtag)
                # if the latest good build is found
                if allartifacts is not None:
                    # if PUT is not flashed by the latest good build
                    flashedby = self.isFlashedBy(artifactname)
                    if not flashedby or force:
                        if not (flashedby & newbuild):
                            buildname = artifactname.replace('.tar.gz','').replace('.tar.bz2','') \
                                                    .replace('.tgz','').replace('fastboot_','')
                            try:
                                buildpath, artifactname = localstorage.getLocalStorageBuild(buildtag=buildname,
                                                                                            factory=factory)
                            except Exception as e:
                                self.syslogger.exception(e)
                                self.logger.error(e)
                                # downloading build
                                buildserver.download_artifact(allartifacts, artifactname, localstorage.localpath)
                                buildpath, artifactname = localstorage.getLocalStorageBuild(buildtag=buildname,
                                                                                            factory=factory)
                            self.flash(localpath=buildpath, artifactname=artifactname, erase=erase,
                                       waitidle=waitidle, checkerrors=checkerrors, 
                                       flashtimeout=flashtimeout, waittimeout=waittimeout)
                            flashednew = True
                    else:
                        self.logger.warn('Latest build already flashed on device !')
            if not flashednew and newbuild:
                raise BuildNotFoundError('New build not found !')
            if buildpath is None:
                raise BuildNotFoundError('Build not found !')
        except Exception as e:
            self.syslogger.exception(e)
            if CONFIG.DEBUG:
                self.logger.exception(e)
            raise
        else:
            # update jenkins Job
            if CONFIG.JENKINS is not None:
                try:
                    from libs.jenkins import JenkinsAPI
                    jenkins = JenkinsAPI()
                    self.prop.updateDeviceInfo()
                    # update build name and description
                    jenkins.updateBuildNameAndDescription('%s_%s_%s' % (CONFIG.DEVICE.BUILD_TYPE.upper() or 'N/A',
                                                                        CONFIG.DEVICE.BUILD_RELEASE.upper() or 'N/A',
                                                                        CONFIG.DEVICE.BUILD_VERSION.upper() or 'N/A'),
                                                          '%s %s (%s) %s' % (CONFIG.DEVICE.CPU_HW.upper() or 'N/A',
                                                                             CONFIG.DEVICE.DEVICE_NAME.upper(),
                                                                             'x64' if CONFIG.DEVICE.CPU_64_BIT
                                                                             else 'x32', CONFIG.DEVICE.SERIAL.upper()))
                except Exception as e:
                    self.logger.error(e)
                    self.syslogger.exception(e)
        finally:
            if rmdir and buildpath is not None and artifactname is not None:
                self.logger.info('Removing "%s"...' % os.path.join(buildpath, artifactname))
                shutil.rmtree(os.path.join(buildpath, artifactname), ignore_errors=True)
                self.logger.done()
        return buildpath, artifactname
