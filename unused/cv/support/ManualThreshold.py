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
#template_dir = current_dir + 'template' + os.sep

class ManualThreshold(object):
    """ detect color by hsv spector. in fact opencv using BGR system """
    def __init__(self):
        self.image = cv2.imread(current_dir + 'Smartbench.png')     
        self.image = cv2.resize(self.image, (600,600))
        self.type = 0
        
    def threshold(self, image):
        img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if self.blur > 0:
            if self.blur%2 == 0: self.blur += 1
            print 'Blur {}'.format(self.blur)
            img = cv2.GaussianBlur(np.copy(img),(self.blur,self.blur),0)
        
        if self.type == 0:
            print 'threshold -> THRESH_BINARY -> {} {}'.format(self.Vmin, self.Vmax)
            return cv2.threshold(img, self.Vmin, self.Vmax, cv2.THRESH_BINARY)[1]
        if self.type == 1:
            print 'threshold -> THRESH_BINARY_INV -> {} {}'.format(self.Vmin, self.Vmax)
            return cv2.threshold(img, self.Vmin, self.Vmax, cv2.THRESH_BINARY_INV)[1]
        if self.type == 2:
            print 'threshold -> THRESH_TRUNC -> {} {}'.format(self.Vmin, self.Vmax)
            return cv2.threshold(img, self.Vmin, self.Vmax, cv2.THRESH_TRUNC)[1]
        if self.type == 3:
            print 'threshold -> THRESH_TOZERO -> {} {}'.format(self.Vmin, self.Vmax)
            return cv2.threshold(img, self.Vmin, self.Vmax, cv2.THRESH_TOZERO)[1]
        if self.type == 4:
            print 'threshold -> THRESH_TOZERO_INV -> {} {}'.format(self.Vmin, self.Vmax)
            return cv2.threshold(img, self.Vmin, self.Vmax, cv2.THRESH_TOZERO_INV)[1]
        if self.type > 4:
            if self.Vmin%2 == 0: self.Vmin += 1
        if self.type == 5:
            print 'adaptiveThreshold -> ADAPTIVE_THRESH_GAUSSIAN_C+THRESH_BINARY -> {} {}'.format(self.Vmin, self.Vmax)
            return cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, self.Vmin, self.Vmax)
        if self.type == 6:
            print 'adaptiveThreshold -> ADAPTIVE_THRESH_GAUSSIAN_C+THRESH_BINARY_INV -> {} {}'.format(self.Vmin, self.Vmax)
            return cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, self.Vmin, self.Vmax)
        if self.type == 7:
            print 'adaptiveThreshold -> ADAPTIVE_THRESH_MEAN_C+THRESH_BINARY -> {} {}'.format(self.Vmin, self.Vmax)
            return cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, self.Vmin, self.Vmax)
        if self.type == 8:
            print 'adaptiveThreshold -> ADAPTIVE_THRESH_MEAN_C+THRESH_BINARY_INV -> {} {}'.format(self.Vmin, self.Vmax)
            return cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, self.Vmin, self.Vmax)
                      
    def manualThreshold(self):
        """ manual detect color """
        
        self.Vmin, self.Vmax, self.type, self.blur = 10,256,0,0
            
        cv2.namedWindow('result')
        cv2.namedWindow('range')
                
        cv.CreateTrackbar("Vmin", "result", self.Vmin, 256, self.__trackbarVmin);
        cv.CreateTrackbar("Vmax", "result", self.Vmax, 256, self.__trackbarVmax);
        cv.CreateTrackbar("Type", "result", self.type, 8, self.__trackbarType);
        cv.CreateTrackbar("Blur", "result", self.blur, 20, self.__trackbarBlur);
        
        self.__inRange()
        while True:
            cv2.imshow('result', self.resImage)
            cv2.imshow('range', self.temp)
            key = cv2.waitKey(1)
            if key == 27: break 
            
        cv2.destroyAllWindows()
        
    def __inRange(self):
        self.resImage = np.copy(self.image)
        self.temp = self.threshold(self.resImage)
        tm = np.copy(self.temp)
        contours, hierarchy = cv2.findContours(tm, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)        
        if len(contours) > 0:
            cv2.drawContours(self.resImage, contours, -1, (0,255,0), 1)
        
    def __trackbarVmin(self, pos):
        self.Vmin = pos
        self.__inRange()

    def __trackbarVmax(self, pos):
        self.Vmax = pos
        self.__inRange()
        
    def __trackbarType(self, pos):
        self.type = pos
        self.__inRange()
    
    def __trackbarBlur(self, pos):
        self.blur = pos
        self.__inRange()
        
if __name__ == "__main__":
    ManualThreshold().manualThreshold()