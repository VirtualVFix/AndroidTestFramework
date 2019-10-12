# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Aug 11, 2017 12:20:00 PM$"

import os
import sys
from io import StringIO
from config import CONFIG
from jenkinsapi.jenkins import Jenkins
from libs.core.logger import getLoggers
from libs.build.base.config import BUILD_SERVER, BUILD_SERVER_NAME, BUILD_SERVER_PASSWORD


class BuildServer(Jenkins):
    """ Class for BuildServer """
    
    def __init__(self, url=BUILD_SERVER, username=BUILD_SERVER_NAME, password=BUILD_SERVER_PASSWORD):
        """
        Args:
            url (str): Url of the build server
            username (str): Username
            password str): Paswword
        """
        
        Jenkins.__init__(self, url, username, password)
        self.logger, self.syslogger = getLoggers(__file__)
        
    def check_latest_good_build(self, jobname, buildqu=None):
        """
        Function to check the latest good build on Jenkins

        Args:
            jobname (str): Jenkins job name
            buildqu (str): Build qualifier - additional info to qualify a build (for example, "device_3uk_oem")
                (it is very useful for retail builds when there are several artifacts in one build)

        Returns:
            tuple: (None, None) or a found artifact (tuple - the dict of all artifacts, the name of the found artifact)
        """ 
        
        result = None, None
        self.logger.newline()
        self.logger.info('Searching the latest good build in "%s (%s)"' % (jobname, buildqu))
        try:            
            build = self[jobname].get_last_good_build()
            # select artifacts which names start with "fastboot_" and contain "buildqu" qualifier
            artifactdict = build.get_artifact_dict()
            if buildqu == "None": 
                artifact = [n for n in artifactdict.keys() if n.startswith('fastboot_')]
            else:                 
                artifact = [n for n in artifactdict.keys() if (n.startswith('fastboot_') and n.count(buildqu) != 0)]

            if len(artifact) == 0:
                raise Exception('There is no latest good build %s' % (' for "%s"'%buildqu if buildqu is not None else ''))
            elif len(artifact) > 1:
                raise Exception("There are more than 1 latest good build")
            
            result = artifactdict, artifact[0]
            self.logger.info('Found "%s" build'%artifact[0])
        except Exception as e:
            self.syslogger.exception(e)
            raise
            
        self.logger.info('Done')
        return result
    
    def download_artifact(self, artifactdict, artifactname, destpath):
        """
        Function to download an artifact from Jenkins

        Args:
            artifactdict (dict): Artifact dict
            artifactname (str): Name of the target artifact
            destpath (str): Path to where the artifactname has to be downloaded

        Return:
            bool: Successfulness of the downloading
        """
        result = False
        self.logger.newline()
        self.logger.info('Start to download "%s"...' % artifactname)
        try:
            # using StringIO to redirect output for save_to_dir - this is a workaround
            # to avoid an unappropriated jenkinsapi's error message which does not affect downloading, but affects subsequent logging
            sys.stderr = StringIO()
            self.logger.newline()
            self.logger.info('Build URL: %s' % artifactdict[artifactname].url)
            self.logger.newline()
            artifactdict[artifactname].save_to_dir(destpath)
            info = sys.stderr.getvalue().replace('\n', '').strip()
            if info != '':
                self.logger.warning("Additional download info: " + info)
            result = os.path.isfile(os.path.join(destpath, artifactname))
        except Exception as e:
            self.syslogger.exception(e)
            if CONFIG.DEBUG:
                self.logger.exception(e)
            raise
        finally:
            sys.stderr = sys.__stderr__
            
        self.logger.info('Build saved in "%s"'%os.path.join(destpath, artifactname))
        self.logger.info('Done')
        return result
