# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 10, 2017 2:26:56 PM$"

import re
import base64
from config import CONFIG
from urllib.parse import urlencode
from http.cookiejar import CookieJar
from libs.core.logger import getLoggers
from libs.jenkins.base.exceptions import JenkinsError
from urllib.request import Request, build_opener, HTTPCookieProcessor, HTTPHandler


class JenkinsAPI:
    def __init__(self):
        self.logger, self.syslogger = getLoggers(__file__)
        cookie = CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(cookie),
                                   HTTPHandler(debuglevel=1 if CONFIG.SYSTEM.SDEBUG else 0))
        self.headers = {'Accept-Charset': 'windows-1251,utf-8;q=0.7,*;q=0.3', 
                        'Accept-Language': 'en-US,en;q=0.8', 
                        'Accept-Encoding': 'gzip, deflate', 
                        'Content-Type': 'application/x-www-form-urlencoded', 
                        'Connection': 'keep-alive', 
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                      + 'Chrome/57.0.2987.133 Safari/537.36'}

    def _getParseJenkinsOptionLine(self):
        """ parse Jenkins option line specified in --jenkins option 
            Returns: userid, token, build url
        """
        user, token, build = None, None, None
        if CONFIG.JENKINS.INTEGRATE is None:
            raise JenkinsError('Jenkins option line [--jenkins] is not specified !')
        
        # check by user:token:build
        match_text = re.search('\s*(.*?)\s*:\s*(.*?)\s*:\s*(http:.*)', CONFIG.JENKINS.INTEGRATE, re.I)
        # check by base64encode:build
        if match_text:
            user, token, build = match_text.groups()
        else:
           match_encode = re.search('\s*(.*?)\s*:\s*(.*)', CONFIG.JENKINS.INTEGRATE, re.I)
           if match_encode:
               user, build = match_encode.groups()
        
        if user is None or build in ['', None]:
            raise JenkinsError('Wrong jenkins option line [--jenkins] format.')
        self.syslogger.info('Jenkins option line: {}:{}:{}'.format(user, token, build))
        
        return user, token, build     
    
    def _sendRequest(self, user, token, url, data):
        """ send update request to Jenkins """
        request = Request(url, data=data, headers=self.headers)
        request.add_header('Authorization', 
                           'Basic ' + (base64.b64encode('{}:{}'.format(user, token)) if token is not None else user))
        # self.sys_logger.info('Jenkins headers: {}'.format(request.headers))
        connection = self.opener.open(request)
        if connection.code == 200:
            self.logger.info('Done.')
        else: 
            raise JenkinsError('Jenkins update reqest return "{}" code.'.format(connection.code))
    
    def checkSerialNumberInURL(self):
        """ check if devie or warthog serial number exists in jenkins build url """
        self.logger.info('Check for device or switchboard serial number in Jenkins build URL...')
        user, token, url = self._getParseJenkinsOptionLine()
        if CONFIG.DEVICE.SERIAL.lower() not in url.lower():
            if CONFIG.SWITCH.SERIAL is None or CONFIG.SWITCH.SERIAL.lower() not in url.lower():
                raise JenkinsError('Device or switchboard serial number not found in Jenkins build URL !')
        self.logger.info('Done.')
    
    def updateBuildNameAndDescription(self, displayname=None, description=None):
        """ Update build display name and builkd display description via REST Jenkins API """
        try:
            self.logger.info('Updating Jenkins build display name and description...')
            user, token, url = self._getParseJenkinsOptionLine()
            self.logger.info('Jenkins build URL: ' + url)
            
           # if build_name is None:
           #     build_name = '%s_%s_%s_%s'%(CONFIG.DEVICE.BUILD_TYPE.upper() or 'N/A',
           #                                 CONFIG.DEVICE.BUILD_RELEASE.upper() or 'N/A',
           #                                 CONFIG.DEVICE.BUILD_VERSION.upper() or 'N/A')
            
            build_number = [x for x in url.split('/') if x not in ['', '/']][-1]
            data = urlencode({'Submit':'save',
                              'json':'{"displayName": "#' + build_number + ' ' + displayname + '", \
                                       "description": "' + description + '"}'})
           # self.sys_logger.info('Jenkins data: {}'.format(data))
            self._sendRequest(user, token, url+'/configSubmit', data)
        except Exception as e:
            self.syslogger.exception(e)
            if CONFIG.SYSTEM.DEBUG:
                raise
            self.logger.error(e)
            
    # def updateBuildDisplayNameAndDescription(self):
    #     self.updateBuildDisplayNameAndDescription('{}_{}_{}'.format(CONFIG.DEVICE.BUILD_TYPE.upper() or 'N/A', CONFIG.DEVICE.BUILD_RELEASE.upper() or 'N/A', CONFIG.DEVICE.BUILD_VERSION.upper() or 'N/A'),
    #                                                         '{} {} ({}) {}'.format(CONFIG.DEVICE.CPU_HW.upper() or 'N/A', CONFIG.DEVICE.DEVICE_NAME.upper(), 'x64' if  CONFIG.DEVICECPU_64_BIT else 'x32', CONFIG.DEVICE.SERIAL.upper()))
        
    def updateJobDescription(self, text):
        """ Update Jenkins Job description """
        try:
            self.logger.info('Updating Jenkins Job description...')
            user, token, url = self._getParseJenkinsOptionLine()
            url = 'http://' + '/'.join([x for x in url.split('/') if x not in ['', '/']][1:-1])+'/'
            data = urlencode({'Submit':'save',
                              'description': text})
            self.logger.info('Jenkins job URL: ' + url)
            self._sendRequest(user, token, url+'/submitDescription', data)       
        except Exception as e:
            self.syslogger.exception(e)
            if CONFIG.SYSTEM.DEBUG:
                raise
            self.logger.error(e)
