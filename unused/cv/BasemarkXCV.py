# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 28, 2016 12:18:18 PM$"

import cv2
from CV import CV
import numpy as np
import cv2.cv as cv
#from config import CONFIG
import libs.logger as logger

class BasemarkXCV(CV):
    """ get ditig from screenshot """
    def __init__(self):
        super(BasemarkXCV, self).__init__()
        self.IMAGE_NAME = 'BasemarkX'
        self.CROP_AREA = [(0.24,0.24), (0.725, 0.575)]
        self.logger = logger.getLogger(__file__) # main logger
#        self.sys_logger = logger.getLogger('sys', 'sys.log', propagate=False) # sys logger
    
    def step3PrepareImage(self, image):
        img = np.copy(image)
        # select digit by color
        img = cv2.inRange(cv2.cvtColor(img, cv2.COLOR_RGB2HSV), cv.CV_RGB(0,0,0), cv.CV_RGB(20, 256, 180))
        # binary crop image
        threshold = cv2.threshold(img, 85, 255, cv2.THRESH_BINARY)[1]
        return threshold
    
    def step4GetDigitArea(self, image):
        # get symbol contours
        binary_image = np.copy(image)
        contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_CCOMP , cv2.CHAIN_APPROX_SIMPLE)
        
        hierarchy = hierarchy[0] # get the actual inner list of hierarchy descriptions
        # For each contour, find the bounding rectangle and draw it
        sample_area = [] # keep symbol rect
        for component in zip(contours, hierarchy):
            currentContour = component[0]
            currentHierarchy = component[1]
            x,y,w,h = cv2.boundingRect(currentContour)
            if currentHierarchy[2] > 0 or currentHierarchy[3] < 0: sample_area.append((x,y,w,h))
        sample_area = sorted(sample_area, key=lambda x:x[0]) # sort sample areas
        return [sample_area]  
    
#    def getDigits(self, image_path):
#        try:
#            image = cv2.imread(image_path)
#            digit = super(BasemarkXCV, self).getDigits(image)
#            if not self.DEBUG:
#                if len(digit) == 0 or len(digit[0]) > 7 or len(digit[0]) < 3: raise Exception, 'Result: "{}" not in valid range !'.format(digit)
#            return digit[0]
#        except Exception, e:
#            if CONFIG.DEBUG: self.logger.exception('Results cannot be recognized !' + str(e))
#            self.sys_logger.exception('Results cannot be recognized !' + str(e))
#            raise Exception, 'Results cannot be recognized ! ' + str(e)