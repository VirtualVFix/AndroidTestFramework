# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Nov 27, 2017 11:27:00 PM$"

try: import cv2
except: pass
from config import CONFIG
from libs.logger import logger

class CameraError(Exception):
    """ Exeption class """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Camera(object):
    def __init__(self, device=0):
        self.camera = cv2.VideoCapture(device)
        self.settings = {'contrast':0, 'brightness':0, 'exposure':0, 'saturation':0, 'gain':50}
        if self.camera.isOpened(): # Try to get the first frame
            retval, frame = self.camera.read()
        else: 
            raise CameraError, 'Camera "{}" initialize error !'.format(device)
        
        self.logger = logger.getLogger(__file__)
        self.sys_logger = logger.getLogger('sys', 'sys.log', propagate=False)
        
    def add(self, setting, value):
        """ add value to setting """
        self.settings[setting] += value
        self.__set(setting, self.settings[setting])

    def get(self, setting):
        """ get camera setting """
        try:
            val = self.camera.get(eval('cv2.CAP_PROP_{0}'.format(setting.upper())))
            self.settings[setting] = val
            return val
        except Exception, e:
            self.sys_logger.exception(e)
            self.logger.error('Getting camera property: "%s" is failed: %s' % (setting, e))
            if CONFIG.DEBUG:
                raise CameraError, e

    def __set(self, setting, value):
        """ set camera setting """
        try:
            self.camera.set(eval('cv2.CAP_PROP_%s' % (setting.upper())), value)
            self.logger.info('Setting camera property: %s: %s' % (setting, value))
        except Exception, e:
            self.sys_logger.exception(e)
            self.logger.error('Setting camera property: "%s" with add value: "%s" is failed: %s' % (setting, value, e))
            if CONFIG.DEBUG:    
                raise CameraError, e

    def read(self):
        """ get frame from camera """
        return self.camera.read()

    def release(self):
        """ release camera """
        return self.camera.release()
    