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

class OctaneCV(CV):
    """ get ditig from screenshot """
    def __init__(self):
        super(OctaneCV, self).__init__()#'basemarkx')
        self.IMAGE_SCALE = 1
        self.logger = logger.getLogger(__file__) # main logger
#        self.sys_logger = logger.getLogger('sys', 'sys.log', propagate=False) # sys logger
    
    def step2CropImage(self, image):
        # find area to crop by color
        color_area = np.copy(image)
        color_area = cv2.inRange(cv2.cvtColor(color_area, cv2.COLOR_RGB2HSV), cv.CV_RGB(210,160,90), cv.CV_RGB(256, 195, 130))

        # find max contour
        contours, hierarchy = cv2.findContours(np.copy(color_area), cv2.RETR_CCOMP , cv2.CHAIN_APPROX_SIMPLE)
        maxArea = 0
        maxContour = None
        for cont in contours:
            _area = cv2.contourArea(cont)#np.int0(cv2.cv.BoxPoints(cv2.minAreaRect(cont))))
            if  _area > maxArea: 
                maxArea = _area
                maxContour = cont
        # get crop area
        x,y,w,h = cv2.boundingRect(maxContour)
        self.CROP_AREA = [(float(x)/image.shape[1], float(y)/image.shape[0]), \
                           (float(x+w)/image.shape[1], float(y+h)/image.shape[0])]
                           
        # crop image by diti area
        img = super(OctaneCV, self).step2CropImage(image)
        # crop again
        self.CROP_AREA = [(0.1,0),(0.9,1)]
        return super(OctaneCV, self).step2CropImage(img)
    
    def step3PrepareImage(self, image):
        img = np.copy(image)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # binary crop image
        threshold = cv2.threshold(img, 155, 255, cv2.THRESH_BINARY_INV)[1]
        return threshold
    
    def step4GetDigitArea(self, image):
        # get symbol contours
        binary_image = np.copy(image)
        contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_CCOMP , cv2.CHAIN_APPROX_SIMPLE)
        hierarchy = hierarchy[0] # get the actual inner list of hierarchy descriptions
        # For each contour, find the bounding rectangle and draw it
        _sample_area = [] # keep symbol rect
        for component in zip(contours, hierarchy):
            currentContour = component[0]
            currentHierarchy = component[1]
            if currentHierarchy[2] > 0 or currentHierarchy[3] < 0: _sample_area.append(cv2.boundingRect(currentContour))
        _sample_area = sorted(_sample_area, key=lambda x:x[1]) # sort by Y
        # find lower string
        sample_area = []
        _max = max([x[1]+x[3] for x in _sample_area]) # find max Y+H
        for rect in _sample_area:
            if rect[1]+rect[3] >= _max-rect[3]*0.1: sample_area.append(rect)
        sample_area = sorted(sample_area, key=lambda x:x[0])
        return [sample_area]
    
#    def getDigits(self, image_path):
#        try:
#            image = cv2.imread(image_path)
#            digit = super(OctaneCV, self).getDigits(image)
#            if not self.DEBUG:
#                if len(digit) == 0 or len(digit[0]) < 2 or len(digit[0]) > 6: raise Exception, 'Result: "{}" not in valid range !'.format(digit)
#            return digit[0]
#        except Exception, e:
#            if CONFIG.DEBUG: self.logger.exception('Results cannot be recognized !' + str(e))
#            self.sys_logger.exception('Results cannot be recognized !' + str(e))
#            raise Exception, 'Results cannot be recognized ! ' + str(e)