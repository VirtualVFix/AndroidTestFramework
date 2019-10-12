# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__="VirtualV <https://github.com/virtualvfix>"
__date__ = "$Aug 11, 2017 12:20:00 PM$"

import os
import tarfile
import platform
from config import CONFIG
from time import time, sleep
from libs.core.logger import getLoggers
from libs.build.base.exceptions import BuildNotFoundError, BuildUnpackError, BuildDownloadError
from libs.build.base.config import SHOW_UNPACK_PROCESS, FILE_TO_FLASH_LINUX, FILE_TO_FLASH_WINDOWS


class LocalStorage:
    """ Class for LocalStorage """
    
    def __init__(self, localpath=None):
        """
        Args:
            localstoragepath (str, default None): Full path to build or folder with builds or None

        Note:
            localstoragepath = CONFIG.BUILD_PATH (--build launch option) if localstoragepath is None
            or CONFIG.BUILD_FOLDER if CONFIG.BUILD_PATH == ''
        """
        self.localpath  = localpath if localpath not in ['', None] else CONFIG.BUILD_PATH \
            if CONFIG.BUILD_PATH not in ['', None] else CONFIG.BUILD_FOLDER
                          
        if self.localpath is None or self.localpath.strip() == '': 
            raise BuildNotFoundError('Build path not specified !')
        if not os.path.exists(self.localpath): 
            raise BuildNotFoundError('Build path "{}" is not found !'.format(self.localpath))
        
        self.logger, self.syslogger = getLoggers(__file__)
       
    def unpack(self, root, archivename, destdir=None):
        """
        Function to unpack an artifact into a directory.

        Args:
            archivename: (str): Name of artifact (build)
            destdir: (str): Directory where the artifact will be unpacked
                (if None it will be unpacked into the root of the local storage)

        Returns:
            full path to unpacked folder or raise error
        """  
        arc_file = None 
        
        arch_fullpath = os.path.join(root, archivename)
        dest_fullpath = root if destdir == None else os.path.join(root, destdir)
        
        unpacked_name = None
        self.logger.newline()
        self.logger.info('Unpacking "%s" archive...'%archivename)
        try:
            # There is an implementation for tar files 
            if tarfile.is_tarfile(arch_fullpath):
                arc_file = tarfile.open(arch_fullpath)
                unpacked_name = arc_file.members[0].name
                
                if SHOW_UNPACK_PROCESS:
                    for f in arc_file:
                        self.logger.info("Extracting: %s %d" % (f.name, f.size))
                        arc_file.extract(f, dest_fullpath)
                        self.logger.info("Extracted: %s %d" % (f.name, f.size))
                else:
                    arc_file.extractall(dest_fullpath)
            else:
                raise BuildUnpackError('"%s" is not a supported archive' % archivename)
        except Exception as e:
            self.logger.error(e)
            self.syslogger.exception(e)
            raise
        finally:
            if arc_file is not None:
                arc_file.close()
            
        self.logger.info('Done')
        return os.path.join(dest_fullpath, unpacked_name)

    def _waitForBuildDownload(self, folder, archive):
        t = time()
        self.logger.newline()
        self.logger.warn('Wait for build downloading complete. Time limit: %d sec.' % CONFIG.BUILD_DOWNLOAD_WAIT_TIME)
        while time()-t < CONFIG.BUILD_DOWNLOAD_WAIT_TIME:
            if os.path.exists(os.path.join(folder,archive)): 
                self.logger.info('Downloading is completed.')
                return archive
            sleep(60)
        raise BuildDownloadError('Wait for build download timeout expired !')
        
    def isBuild(self, localpath):
        """ check if flash script exists in folder """
        result = False
        if os.path.exists(os.path.join(localpath, (FILE_TO_FLASH_WINDOWS if 'window' in platform.system().lower()
                                                   else FILE_TO_FLASH_LINUX))):
            result = True
        return result
    
    def getLocalStorageBuild(self, localpath=None, buildtag=None, factory=False):
        """
        Find build by buildtag, device or product name.
        Find late added build in self._lpath if self._lpath is directory.
        Unpack build if required.

        Args:
            localpath (str): Full path to local storage to search build
            buildtag (str): Build tag like "nash_oem"
            factory (bool, default False): Check **factory_** prefix in build name

        Raises:
            :class:`.base.exceptions.BuildNotFoundError` when build not found

        Returns:
            tuple: (full path to root of build folder, build folder name) or raise Exception when build not found
        """
        result_path = None
        
        if localpath is None:
            localpath = self.localpath

        # build name
        if buildtag is None:
            buildtag = CONFIG.DEVICE_NAME.split('_')[0].lower() or \
                       CONFIG.DEVICE_PRODUCT.split('_')[0].lower() or \
                       CONFIG.BUILD_PRODUCT.split('_')[0].lower()

        # factory build
        if factory: 
            buildtag = 'factory_' + buildtag
        
        # if path to directory
        if os.path.isdir(localpath):
            if self.isBuild(localpath):
                result_path = localpath
            else:  # search latest added build in folder
                _files = []
                self.logger.info('Searching for latest build in [%s] local storage by [%s] tag...'
                                 % (localpath, buildtag))
                for x in os.listdir(localpath):
                    if 'factory' in x.lower() and not factory: 
                        continue
                    if (buildtag.lower() in x.lower() or x.lower() == buildtag.lower()) \
                        and (os.path.isdir(os.path.join(localpath, x)) or x.endswith(('.tar.bz2', '.tar.gz', '.tgz'))):
                        _files.append(x)
                if len(_files) == 0: 
                    raise BuildNotFoundError('Build not found')
                # get latest added build
                build_path = os.path.join(localpath, sorted(_files, key=lambda x: os.stat(os.path.join(localpath, x))
                                                            .st_ctime)[::-1][0])
                return self.getLocalStorageBuild(localpath=build_path, buildtag=buildtag, factory=factory)
        else:
            folder, archive = os.path.split(localpath)
            folder += os.sep
            # waiting if buld dowloading in progress
            if archive[:archive.rfind('.')].endswith(('.bz2', '.gz', '.tgz')):
                archive = self._waitForBuildDownload(folder, archive[:archive.rfind('.')])    
            # if build is tar archive
            build_path = self.unpack(folder, archive)
            return self.getLocalStorageBuild(localpath=build_path, buildtag=buildtag, factory=factory)
        
        if result_path is None: 
            raise BuildNotFoundError('Build for "{}" was not found in "{}"'.format(buildtag, localpath))
        self.logger.info('Build path: "%s"'%result_path)
        bulid_path, build_name = os.path.split(result_path if not result_path.endswith(os.sep) else result_path[:-1])
        return bulid_path, build_name
