# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 28, 2016 12:18:18 PM$"

import os
import cv2
import sys
import numpy as np
from time import time
from BasemarkXCV import BasemarkXCV

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__)) + os.sep
IMAGE_PATH = 'D:\\screenshots' + os.sep
IMAGE_NAME = 'BasemarkX'
IMAGE_CHANGE_TIME = 2.0

class CVBasemarkXTest(BasemarkXCV):
    """ Test class for recognition debug """
    
    def __init__(self):
        super(CVBasemarkXTest, self).__init__()
        self.image_list = []
        for dirs,subs,files in os.walk(IMAGE_PATH):
            for file in files:
                if IMAGE_NAME.lower() in file.lower():
                    self.image_list.append(file)
        self.textarray = [('image', None),
                          ('image count', None),
                          ('select', None)]
                          
        self.IMAGE_SCALE = 1.5
        self.DEBUG = True

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
            cv2.putText(image, '{0}: {1}'.format(x[0].upper(), x[1]), (10, i), fontFace = cv2.FONT_HERSHEY_DUPLEX, fontScale = fontScale, color=color)
            i += 15

    def main(self):
        try:            
            # crate window            
            cv2.namedWindow('original_image')
#            cv2.namedWindow('scale_image')
            cv2.namedWindow('crop_image')
            cv2.namedWindow('prepare_image')
            cv2.namedWindow('SAMPLES')
            
            current_img = -1
            current_time = time()
            just_start = True
            digit = -1 # selected digit
            while True:
                # load image by time or current selection
                if (time()-current_time >= IMAGE_CHANGE_TIME or just_start):
                    just_start = False
                    # load image
                    digit = self.getDigits(IMAGE_PATH + self.image_list[current_img%len(self.image_list)])
#                    image = cv2.imread(IMAGE_PATH + self.image_list[current_img%len(self.image_list)])
                    current_img += 1
                    current_time = time()
                    self.editText('image', self.image_list[current_img%len(self.image_list)])
                    self.editText('image count', str(current_img)+'/'+str(len(self.image_list)))
                #===============================================================                
                # get digit
                self.editText('Digit', digit)
                for grp in self.DEBUG_DATA['area_group_list']:
                    for x,y,w,h in grp:
                        cv2.rectangle(self.DEBUG_DATA['crop_image'], (x,y), (x+w,y+h), (0,255,0), 1)
                
                # concantinate all samples to one imagee
                _tm = []
                for grp in self.DEBUG_DATA['sample_group_list']:
                    _tm.append(np.concatenate([x for x in grp], axis=1))
                sample = np.concatenate([x for x in _tm], axis=1)

                self.drawText(self.DEBUG_DATA['crop_image'], color = (0,0,255))
                cv2.imshow('original_image', self.DEBUG_DATA['original_image'])
#                cv2.imshow('scale_image', self.DEBUG_DATA['scale_image'])
                cv2.imshow('crop_image', self.DEBUG_DATA['crop_image'])
                cv2.imshow('prepare_image', self.DEBUG_DATA['prepare_image'])
                cv2.imshow('SAMPLES', sample)

                # key event
                key = cv2.waitKey(1)
                if key == 27: break # esc
                elif key >= 0: print 'KEY PRESSED: ' + str(key) + ' - ' + chr(key)
        finally:
            cv2.destroyAllWindows()

if __name__ == "__main__":
    CVBasemarkXTest().main()