# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 28, 2016 12:18:18 PM$"

import cv2
from CV import CV
import numpy as np
#from config import CONFIG
import libs.logger as logger

WIDTH,HEIGHT=1,0

class ElectopiaCV(CV):
    """ get ditig from screenshot """
    def __init__(self):
        super(ElectopiaCV, self).__init__()#'electopia')
        self.IMAGE_SCALE = 0.3
        self.CROP_AREA = [(0.277, 0.267), (0.659, 0.738)]
        self.logger = logger.getLogger(__file__) # main logger
#        self.sys_logger = logger.getLogger('sys', 'sys.log', propagate=False) # sys logger
    
    def step2CropImage(self, image):
        # crop image by CROP_AREA
        frame = super(ElectopiaCV, self).step2CropImage(image)
        
        # find score filed
        img = np.copy(frame)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        threshold = cv2.threshold(img, 90, 256, cv2.THRESH_BINARY_INV)[1]
        
        # find max contour
        contours, hierarchy = cv2.findContours(threshold, cv2.RETR_CCOMP , cv2.CHAIN_APPROX_SIMPLE)
        maxArea = 0
        maxContour = None
        for cont in contours:
            _area = cv2.contourArea(cont)
            if  _area > maxArea: 
                maxArea = _area
                maxContour = cont
        
        # get crop area
        x,y,w,h = cv2.boundingRect(maxContour)
        self.CROP_AREA = [(float(x)/frame.shape[WIDTH], float(y)/frame.shape[HEIGHT]), \
                           (float(x+w)/frame.shape[WIDTH], float(y+h)/frame.shape[HEIGHT])]
        # crop again
        frame = super(ElectopiaCV, self).step2CropImage(frame)
        
        # one more crop
        self.CROP_AREA = [(0.7, 0.16), (0.982, 0.684)]
        return super(ElectopiaCV, self).step2CropImage(frame)
    
    def step3PrepareImage(self, image):
        img = np.copy(image)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # binary crop image
        threshold = cv2.threshold(img, 90, 256, cv2.THRESH_TOZERO)[1]
        return threshold
    
    def step4GetDigitArea(self, image):
        # find contours
        contours, hierarchy = cv2.findContours(np.copy(image), cv2.RETR_CCOMP , cv2.CHAIN_APPROX_SIMPLE)
        hierarchy = hierarchy[0]
        # find outer contour
        _smpl_area = [] # keep symbol rect
        for component in zip(contours, hierarchy):
            currentContour = component[0]
            currentHierarchy = component[1]
            if currentHierarchy[2] > 0 or currentHierarchy[3] < 0: _smpl_area.append(cv2.boundingRect(currentContour))
        _smpl_area = sorted(_smpl_area, key=lambda x:x[1]) # sort by Y

        # group by line and sort by X
        sample_area = []
        sample_area_group = []
        i = 0 
        while i < len(_smpl_area):
            _yh = _smpl_area[i][1]+_smpl_area[i][3] # y+h
            _delta = _smpl_area[i][3]*0.1 # 10% of y+h
            tm = [_smpl_area[i]]
            for j in range(i+1, len(_smpl_area), 1):
                _yh_next = _smpl_area[j][1]+_smpl_area[j][3]
                if _yh+_delta >= _yh_next >= _yh-_delta: 
                    tm.append(_smpl_area[j])
                else: break
            i += 1 if len(tm) == 0 else len(tm)
            for x in sorted(tm, key=lambda x:x[0]): sample_area.append(x)
            sample_area_group.append(sorted(tm, key=lambda x:x[0])) # sort by X
            
        if not self.DEBUG:
            if len(sample_area_group) != 5: raise Exception, 'Digits are not found !'
        return sample_area_group
    
#    def getDigits(self, image_path):
#        try:
#            image = cv2.imread(image_path)
#            digit_list = super(ElectopiaCV, self).getDigits(image)
#            if not self.DEBUG:
#                if '-1' in digit_list: raise Exception, 'One of results: "{}" not in valid range !'.format(digit_list)
#            return digit_list
#        except Exception, e:
#            if CONFIG.DEBUG: self.logger.exception('Results cannot be recognized !' + str(e))
#            self.sys_logger.exception('Results cannot be recognized !' + str(e))
#            raise Exception, 'Results cannot be recognized ! ' + str(e)