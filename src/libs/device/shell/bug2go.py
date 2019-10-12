# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Aug 12, 2015 3:17:27 PM$"

import re
from .base import Base
from libs.core.logger import getLogger
from libs.device.shell.base.exceptions import PathOnDeviceNotFoundError, UtilityError


class Bug2Go(Base):
    def __init__(self, serial):
        super(Bug2Go, self).__init__(serial)
        self.logger = getLogger(__file__)
        self.__bug2go_path = '/data/vendor/bug2go/'
        
    @property
    def bug2GoPath(self):
        return self.__bug2go_path
    
    @bug2GoPath.setter
    def bug2GoPath(self, path):
        self.__bug2go_path = path if path.endswith('/') else '%s/' % path
        
    def bug2GoClear(self, verbose=True):
        """ 
        Clear bug2go logs folder 
        
        Args: 
            verbose (bool): Print message to logger
        """
        if verbose:
            self.logger.info('Clearing bug2go folder...')
            
        self.sh('rm -r %s*' % self.bug2GoPath, errors=False, empty=True)
        
        if verbose:
            self.logger.done()
        
    def searchBug2GoLogs(self, logname=None, regex=None):
        """ 
        Search logs in bug2go folder
        
        Args: 
            logname (str or list): Log name or names list 
            regex (str or list): Regex pattern or patterns list
            
        Returns:
            (log name, path to found log) or (None, None)
        """
        
        if logname is None and regex is None:
            raise PathOnDeviceNotFoundError('Log name or regex pattern not defined !')
        
        logname = [logname] if isinstance(logname, str) else logname
        regex = [regex] if isinstance(regex, str) else regex
        
        out = self.sh('ls %s' % self.bug2GoPath, errors=True, empty=True)
        out = [x.strip() for x in out.split('\n') if x.strip() != '']

        for x in out:
            # search by logname
            if logname is not None:
                for name in logname:
                    if name.lower() in x.lower():
                        return x, self.bug2GoPath
            # search by regex
            if regex is not None:
                for reg in regex:
                    match = re.search(reg, x, re.I)
                    if match: 
                        return x, self.bug2GoPath
        return None, None
    
    def checkBug2GoLogs(self, logname=None, regex=None, exception=UtilityError):
        """ 
        Check bug2go logs and raise exception when found and *exception* specified 
        
        Raises:
           Exception specified in **exception** keyword argument
        """
        name, _ = self.searchBug2GoLogs(logname=logname, regex=regex)
        if name is not None and issubclass(exception, Exception):
            raise exception('[%s] log is detected in Bug2Go folder !' % name)
    