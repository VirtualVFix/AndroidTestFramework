# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Nov 27, 2017 11:27:00 PM$"

import os
import sys
import cv2
import pytz
from time import time
from Camera import Camera
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__)) + os.sep
IMAGE_DIR = current_dir + 'Images' + os.sep
TIME_ZONE = 'Asia/Vladivostok'
IMAGE_NAME_FORMAT = ''

if not os.path.exists(IMAGE_DIR):
    os.mkdir(IMAGE_DIR)

class ManualSetup(object):
    def __init__(self, device=0, interval=5, folder=None):
        self.camera = Camera(device)
        self.interval = interval
        self.folder = folder
        
        raise NotImplementedError, 'Feature is not implemented'
        
        self.textarray = [('contrast', None),
                          ('brightness', None),
                          ('exposure', None),
                          ('saturation', None),
                          ('gain', None),
                          ('fps', 0)]
                          
    def main(self):
        pass
        
    def launch(self):
        """ launch com test """
        global screenshot_dir
        try:
            cv2.namedWindow('Camera')
            retval, frame = self.camera.read()
            fps = 0
            fpsTime = time()
            showFps = 0
            
            if self.folder is not None:
                screenshot_dir += self.folder+os.sep
                if not os.path.exists(screenshot_dir):
                    os.mkdir(screenshot_dir)
            
            for x in self.camera.settings: # camera settings
                self.editText(x, self.camera.get(x))
                
            t = time()
            print 'Press ESC for exit.'
            print 'Press 1-2 for seting Contrast, 3-4 for setting Brightness, 5-6 for setting Exposure, 7-8 for setting Saturation, 9-0 for setting Gain level.'
            while retval: # main cycle  
            
                if time()-fpsTime >= 1: # calculate FPS
                    showFps = fps
                    fps = 0 
                    fpsTime = time()
                    self.editText('fps', showFps)
                fps += 1

                #---------------------------------------------------------------
                for x in self.camera.settings: # camera settings
                    self.editText(x, self.camera.settings[x])
                self.drawText(frame)
                cv2.imshow('Camera', frame)                

                retval, frame = self.camera.read()

                key = cv2.waitKey(1)
                
                def setSetting(setting, value):
                    self.camera.add(setting, value)
                    self.editText(setting, self.camera.settings[x])
                    
                if key == 27: break 
                elif key == 32 or time()-t >= self.interval:
                    tm = '{}{}.jpeg'.format(IMAGE_DIR, 
                                            datetime.now(pytz.timezone(TIME_ZONE)).strftime('%H_%M_%S_%f'))
                    cv2.imwrite(tm, frame)
                    print 'Screenshot saved in {0}'.format(tm)
                    t = time()
                elif key == 49: # 1
                    setSetting('contrast', -1)
                elif key == 50: # 2
                    setSetting('contrast', 1)
                elif key == 51: # 3
                    setSetting('brightness', -1)
                elif key == 52: # 4
                    setSetting('brightness', 1)
                elif key == 53: # 5
                    setSetting('exposure', -1)
                elif key == 54: # 6
                    setSetting('exposure', 1)
                elif key == 55: # 7
                    setSetting('saturation', -1)
                elif key == 56: # 8 
                    setSetting('saturation', 1)
                elif key == 57: # 9 
                    setSetting('gain', -1)
                elif key == 48: # 0 
                    setSetting('gain', 1)
                #---------------------------------------------------------------               
        except Exception, e:
            print 'Error: {0}'.format(e)
            return False, e
        finally:
            cv2.destroyAllWindows()
            self.camera.release()
        return True, ''
    
    def editText(self, name, text):
        """ edit text to screen """
        for i in range(0, len(self.textarray), 1):
            if name in self.textarray[i]: 
                self.textarray[i] = (self.textarray[i][0], text)
                return 
        self.textarray.append((name, text))
                
    def drawText(self, image, fontScale = 0.5, color = (255,255,255)):
        i = 15
        for x in self.textarray:
            cv2.putText(image, '{0}: {1}'.format(str(x[0]), str(x[1])), (10, i), fontFace = cv2.FONT_HERSHEY_TRIPLEX, fontScale = fontScale, color=color)
            i += 15
          
if __name__ == "__main__":
    SimpleTracker(0, 10 if len(sys.argv) == 1 else int(sys.argv[1]), 
                  None if len(sys.argv) == 2 else sys.argv[2]).launch()