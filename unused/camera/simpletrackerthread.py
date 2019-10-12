# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Nov 27, 2017 11:27:00 PM$"

import os
import pytz
try: import cv2
except: pass
import threading
from time import time
from config import CONFIG
from datetime import datetime
from libs.logger import logger
from camera import Camera, CameraError
from constants import SCREENSHOT_PREFIX


class SimpleTrackerThread(threading.Thread):
    def __init__(self, task_queue, device=0, settings = None, interval=None, path=None, folder='camera'):
        """
        Args: 
            device (int, default: 0): Camera number
            settings (dict): Camera settings
            interval (int): Make snapshots via time interval in seconds. Disabled if None
            path (str): full path to folder to save camera snaphots
            folder (str): folder name in log folder if path is None
        """
        super(SimpleTrackerThread, self).__init__()
        # take screenshot tasks 
        self.task_queue = task_queue
        
        raise NotImplementedError, 'Feature is not implemented'
        
        # loggers
        self.logger = logger.getLogger(__file__)
        self.sys_logger = logger.getLogger('sys', 'sys.log', propagate=False)
        
        # create camera
        self.camera = Camera(device)
        
        # set camera settings
        if settings is not None:
            for key in settings:
                if key.lower() not in self.camera.settings:
                    raise CameraError('Property "%s" not found in Camera settings ! ' % key
                                      + 'Allowed the following properties: [%s]'
                                      % (','.join(self.camera.settings.keys())))
                if settings[key] is not None:
                    self.camera.add(key.lower(), settings[key])
        
        # set interval if required
        self.interval = interval if interval is not None and interval > 0 else None
        # create screenshot path
        self.screen_path = path or (os.path.join(CONFIG.LOG_PATH, folder) if folder is not None else CONFIG.LOG_PATH)
        
        # create screenshot folder 
        if not os.path.exists(self.screen_path):
            os.mkdir(self.screen_path)
        
        # text to print
        self.textarray = [('contrast', None),
                          ('brightness', None),
                          ('exposure', None),
                          ('saturation', None),
                          ('gain', None),
                          ('fps', 0)]

    def run(self):
        """ launch camera """        
        try:
            cv2.namedWindow('Camera')
            retval, frame = self.camera.read()
            fps = 0
            fpsTime = time()
            showFps = 0
            
            for x in self.camera.settings: # camera settings
                self.editText(x, self.camera.get(x))
                
            t = time()
            # main cycle
            while retval:
                # calculate FPS
                if time()-fpsTime >= 1: 
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

                # read frame 
                retval, frame = self.camera.read()
                # get task
                next_task = self.task_queue.get()
                print('@@', next_task)
                
                # exit task
                if next_task == 'exit':
#                    self.task_queue = None
                    self.task_queue.task_done()
                    break 
                    
                # space or timer interval or screenshot task
                if next_task is not None and next_task.startswith('screenshot') \
                        or self.interval is not None and time()-t >= self.interval:
                    screen_name = '%s%s.jpeg' % ('' if next_task is None else next_task.split(':')[1],
                                                 datetime.now(pytz.timezone(CONFIG.TIMEZONE)).strftime(SCREENSHOT_PREFIX))
                    screen_path = os.path.join(self.screen_path, screen_name)
                    cv2.imwrite(screen_path, frame)
                    self.logger.info('[%s] screenshot saved' % screen_name)
#                    self.task_queue = None
                    self.task_queue.task_done()
                    t = time()
                #---------------------------------------------------------------               
        except Exception, e:
            self.logger.error('Camera error: %s' % e)
            self.sys_logger.exception(e)
            raise CameraError, e
        finally:
            cv2.destroyAllWindows()
            self.camera.release()
        return
    
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
            