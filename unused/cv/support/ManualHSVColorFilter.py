# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__="VirtualV <https://github.com/virtualvfix>"
__date__ ="$13.02.2014 16:39:38$"

import cv2
import numpy as np 
import cv2.cv as cv
import os

current_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
#current_dir = current_dir[:current_dir.find('support')]
template_dir = current_dir + 'template' + os.sep

class ManualHSVColorFilter(object):
    """ detect color by hsv spector. in fact opencv using BGR system """
    def __init__(self):
        self.image = cv2.imread(current_dir + 'Smartbench.png')     
        self.image = cv2.resize(self.image, (600,600))
                      
    def manualColorFilter(self):
        """ manual detect color """
        self.rgb = np.copy(self.image)
        self.hsv = cv2.cvtColor(self.rgb, cv2.COLOR_RGB2HSV)
        
        self.Hmin, self.Hmax, self.Smin, self.Smax, self.Vmin, self.Vmax = 113,138, 185,256, 90,256#[y for x in [x for x in self._templater.colorFilters[def_color]] for y in x ]
            
        cv2.namedWindow('result')
        cv2.namedWindow('range')
                
        cv.CreateTrackbar("Hmin", "result", self.Hmin, 256, self.__trackbarHmin);
        cv.CreateTrackbar("Hmax", "result", self.Hmax, 180, self.__trackbarHmax);
        cv.CreateTrackbar("Smin", "result", self.Smin, 256, self.__trackbarSmin);
        cv.CreateTrackbar("Smax", "result", self.Smax, 256, self.__trackbarSmax);
        cv.CreateTrackbar("Vmin", "result", self.Vmin, 256, self.__trackbarVmin);
        cv.CreateTrackbar("Vmax", "result", self.Vmax, 256, self.__trackbarVmax);
        
        self.__inRange()
        while True:
            cv2.imshow('result', self.resImage)
            cv2.imshow('range', self.temp)
            key = cv2.waitKey(1)
            if key == 27: break 
            
        cv2.destroyAllWindows()
        
    def __inRange(self):
        self.resImage = np.copy(self.image)
        self.temp = cv2.inRange(self.hsv, cv.CV_RGB(self.Vmin, self.Smin, self.Hmin), cv.CV_RGB(self.Vmax, self.Smax, self.Hmax))
        tm, self.temp = cv2.threshold(self.temp, 85, 255, cv2.THRESH_BINARY)
        tm = np.copy(self.temp)
        contours, hierarchy = cv2.findContours(tm, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)        
        if len(contours) > 0:
            cv2.drawContours(self.resImage, contours, -1, (0,255,0), 2)
        
    def __trackbarVmin(self, pos):
        self.Vmin = pos
        self.__inRange()

    def __trackbarVmax(self, pos):
        self.Vmax = pos
        self.__inRange()

    def __trackbarSmin(self, pos):
        self.Smin = pos
        self.__inRange()

    def __trackbarSmax(self, pos):
        self.Smax = pos
        self.__inRange()

    def __trackbarHmin(self, pos):
        self.Hmin = pos
        self.__inRange()

    def __trackbarHmax(self, pos):
        self.Hmax = pos
        self.__inRange()
        
if __name__ == "__main__":
    ManualHSVColorFilter().manualColorFilter()