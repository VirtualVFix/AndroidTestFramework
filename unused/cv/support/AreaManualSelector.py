# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 28, 2016 12:18:18 PM$"

import os
import cv2
import numpy as np
import cv2.cv as cv
from time import time, sleep

IMAGE_PATH = 'D:\\screenshots' + os.sep
IMAGE_NAME = 'BasemarkX'
IMAGE_CHANGE_TIME = 4.0
IMAGE_SCALE = 2
X,Y=0,1

class CVBasemarkX(object):
    def __init__(self):
        self.image_list = []
        for dirs,subs,files in os.walk(IMAGE_PATH):
            for file in files:
                if IMAGE_NAME.lower() in file.lower():
                    self.image_list.append(file)
        self.textarray = [('image', None),
                          ('rec', None)
                         ]
                    
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
           
    def relative(self, x,y):
        # mouse relative coordinate
        accuracy = 3
        return (round(float(x)/self.width, accuracy), round(float(y)/self.height, accuracy))
    
    def main(self):
        try:
            self.drawing = False # true if mouse is pressed
            self.mouse_rectangle = None
            self.width, self.height = 0, 0

            # mouse callback function
            def draw_rectangle(event, x, y, flags, param):
                if event == cv2.EVENT_LBUTTONDOWN:
                    self.drawing = True
                    self.mouse_rectangle = [self.relative(x,y), self.relative(x,y)]

                elif event == cv2.EVENT_MOUSEMOVE:
                    if self.drawing == True:
                        self.mouse_rectangle[1] = self.relative(x,y)

                elif event == cv2.EVENT_LBUTTONUP:
                    self.drawing = False
                    self.mouse_rectangle[1] = self.relative(x,y)
                    self.editText('rec', self.mouse_rectangle)
                    print self.mouse_rectangle
            
            # crate window
            cv2.namedWindow(IMAGE_NAME)
            cv2.setMouseCallback(IMAGE_NAME, draw_rectangle)
            
            current_img = -1
            current_time = time()
            just_start = True
            while True:
                if time()-current_time >= IMAGE_CHANGE_TIME or just_start:
                    just_start = False
                    frame = cv2.imread(IMAGE_PATH + self.image_list[current_img%len(self.image_list)])
                    self.height, self.width = int(frame.shape[0]/IMAGE_SCALE), int(frame.shape[1]/IMAGE_SCALE), 
                    print frame.shape[0], frame.shape[1], '->', self.height, self.width, self.image_list[current_img%len(self.image_list)]
                    frame = cv2.resize(frame, (self.width,self.height))
                    current_img += 1
                    current_time = time()
                    self.editText('image', self.image_list[current_img%len(self.image_list)])
                    
                image = np.copy(frame)
                
                # draw mouse rectangle
                if not self.mouse_rectangle is None:
                    cv2.rectangle(image, (int(self.mouse_rectangle[0][X]*self.width),int(self.mouse_rectangle[0][Y]*self.height)), \
                                         (int(self.mouse_rectangle[1][X]*self.width),int(self.mouse_rectangle[1][Y]*self.height)), \
                                          thickness = 1, color = (0,255,255))

                self.drawText(image, color = (0,0,255))
                cv2.imshow(IMAGE_NAME, image)

                # key event
                key = cv2.waitKey(1)
                if key == 27: break
        finally:
            cv2.destroyAllWindows()
        

if __name__ == "__main__":
    CVBasemarkX().main()
