# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Apr 28, 2016 12:18:18 PM$"

import os
import sys
import cv2
import numpy as np
import cv2.cv as cv
from time import time, sleep

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__)) + os.sep
IMAGE_PATH = 'D:\\screenshots' + os.sep
IMAGE_NAME = 'BasemarkX'
IMAGE_CHANGE_TIME = 0.5
IMAGE_SCALE = 1.5
WIDTH,HEIGHT=1,0
X,Y=0,1
SYMBOL_SIZE = 32

class CVBasemarkX(object):
    """ Script for lerning digit recognition.
        Use left mouse key for select area on image. 
        This area with relative coordinates will be printed on image in "SELECT" tag. 
        Use 0-9 keys (not numpad) to add responce for current selected area (area will be saved as sample). 
        Responces and samples will be saved to script directory after exit via Esc key.
        Keys: 
            ESC - exit. 
            SpaceBar - skip image. 
            0-9 - digit on slected area (responce for recognition). 
            Backspace - delete previuos responce. 
            Enter - skip selected sample. """
    
    def __init__(self):
        self.image_list = []
        for dirs,subs,files in os.walk(IMAGE_PATH):
            for file in files:
                if IMAGE_NAME.lower() in file.lower():
                    self.image_list.append(file)
        self.textarray = [('image', None),
                          ('image count', None),
                          ('select', None)]
        self.digit_area = [(0.24,0.24), (0.725, 0.575)]
        self.digit_model = None
        if os.path.exists(CURRENT_DIR + IMAGE_NAME.lower() + 'knsamples.data'):
            self.digit_model = cv2.KNearest()
            samples = np.loadtxt(CURRENT_DIR + IMAGE_NAME.lower() + 'knsamples.data',np.float32)
            responses = np.loadtxt(CURRENT_DIR + IMAGE_NAME.lower() + 'knresponses.data',np.float32)
            self.digit_model.train(samples, responses)  

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
    
    def getSample(self, threshold, sample_area, current_selection):
        """ get image sample, resize it and convert it to full binary image """
        sample = threshold[sample_area[current_selection][Y]:sample_area[current_selection][Y]+sample_area[current_selection][3],\
                                            sample_area[current_selection][X]:sample_area[current_selection][X]+sample_area[current_selection][2]]
        sample = cv2.resize(sample, (SYMBOL_SIZE, SYMBOL_SIZE))
        
        # convert image to read binarry (only 0 or 255 color value)
        for i in xrange(len(sample)): 
            for j in xrange(len(sample[i])):
                if sample[i][j] < 255/2: 
                    sample[i][j] = 0
                else: sample[i][j] = 255
#        shape = sample.shape
#        sample = sample.reshape(1, sample.size)
#        for i in xrange(len(sample[0])-1):
#            if sample[0][i] < 255/2: sample[0][i] = 0 
#            else: sample[0][i] = 255
#        sample = sample.reshape(shape[0], shape[1])
        return sample
    
    def recognition(self, samples, nearest=1):
        # recognition digit by sample
        if self.digit_model is None: return -2
        string = ''
        for i in xrange(len(samples)):
            sample = samples[i].reshape((1,samples[i].size))
            sample = np.float32(sample)
            retval, results, neigh_resp, dists = self.digit_model.find_nearest(sample, k=nearest)
            d = int(results[0][0])         
            string += str(d)
        return string if string != '' else -1
    
    def main(self):
#        samples = np.empty((0, SYMBOL_SIZE*SYMBOL_SIZE)) # 32x32 samples size
        samples = []
        responses = []
        try:
            self.drawing = False # true if mouse is pressed
            self.mouse_rectangle = None
            self.width, self.height = 0, 0
            # mouse callback function for draw rectangle
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
                    self.editText('select', self.mouse_rectangle)
                    print self.mouse_rectangle
            
            # crate window
            cv2.namedWindow(IMAGE_NAME)
            cv2.namedWindow(IMAGE_NAME + '2')
            cv2.namedWindow('SAMPLE')
            cv2.setMouseCallback(IMAGE_NAME, draw_rectangle)
            
            current_img = -1
            current_time = time()
            just_start = True
            current_selection = -1 # selected area
            digit = -1 # selected digit
            while True:
                # load image by time or current selection
                if (time()-current_time >= IMAGE_CHANGE_TIME or just_start) and current_selection == -1:
                    current_selection = 0
                    just_start = False
                    # load image
                    frame = cv2.imread(IMAGE_PATH + self.image_list[current_img%len(self.image_list)])
                    print frame.shape[HEIGHT], frame.shape[WIDTH], self.image_list[current_img%len(self.image_list)]
                    
                    # resize and crop image
                    frame = cv2.resize(frame, (int(frame.shape[WIDTH]/IMAGE_SCALE), int(frame.shape[HEIGHT]/IMAGE_SCALE)))
                    frame = frame[int(frame.shape[HEIGHT]*self.digit_area[0][Y]):int(frame.shape[HEIGHT]*self.digit_area[1][Y]), 
                              int(frame.shape[WIDTH]*self.digit_area[0][X]):int(frame.shape[WIDTH]*self.digit_area[1][X])]
#                    frame.reshape(1, frame.size)
                    self.height, self.width = frame.shape[:2]#int(frame.shape[0]/IMAGE_SCALE), int(frame.shape[1]/IMAGE_SCALE)
                    current_img += 1
                    current_time = time()
                    self.editText('image', self.image_list[current_img%len(self.image_list)])
                    self.editText('image count', str(current_img)+'/'+str(len(self.image_list)))
                #===============================================================                
                image = np.copy(frame)
                # crop image
                image2 = cv2.inRange(cv2.cvtColor(image, cv2.COLOR_RGB2HSV), cv.CV_RGB(0,0,0), cv.CV_RGB(20, 256, 180))
                
                # binary crop image
                threshold = cv2.threshold(image2, 85, 255, cv2.THRESH_BINARY)[1]
                
                # get symbol contours
                binary_image = np.copy(threshold)
                contours, hierarchy = cv2.findContours(binary_image, cv2.RETR_CCOMP , cv2.CHAIN_APPROX_SIMPLE)
                hierarchy = hierarchy[0] # get the actual inner list of hierarchy descriptions
                # For each contour, find the bounding rectangle and draw it
                sample_area = [] # keep symbol rect
                for component in zip(contours, hierarchy):
                    currentContour = component[0]
                    currentHierarchy = component[1]
                    x,y,w,h = cv2.boundingRect(currentContour)
                    if currentHierarchy[2] > 0 or currentHierarchy[3] < 0: 
                        sample_area.append((x,y,w,h))
                        cv2.rectangle(image, (x,y), (x+w,y+h), (0,255,0), 1) # parent contour
                    else:
                        cv2.rectangle(image, (x,y), (x+w,y+h), (0,0,255), 1) # child contour
                sample_area = sorted(sample_area, key=lambda x:x[0])
                        
                # get sample of symbol
                if current_selection < len(sample_area): sample = self.getSample(threshold, sample_area, current_selection) 
                
                # recognition image if available
                recog_smpls = []
                for i in xrange(len(sample_area)):
                    recog_smpls.append(self.getSample(threshold, sample_area, i))               
                self.editText('digit', self.recognition(recog_smpls))
                        
                cv2.rectangle(image, (sample_area[current_selection][X],sample_area[current_selection][Y]), \
                                     (sample_area[current_selection][X]+sample_area[current_selection][2],sample_area[current_selection][Y]+sample_area[current_selection][3]), (255,0,255), 2) # draw selected area

#                cv2.drawContours(image, contours, -1, (0,255,0), 2)
                
                # digit area
#                cv2.rectangle(image, (int(self.width*0.24),int(self.height*0.24)), \
#                                     (int(self.width*0.725),int(self.height*0.575)), \
#                                      thickness = 2, color = (0,255,0))
                
#                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#                image = cv2.adaptiveThreshold(image, 250, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 6)
                #===============================================================
                # draw mouse rectangle
                if not self.mouse_rectangle is None:
                    cv2.rectangle(image, (int(self.mouse_rectangle[0][X]*self.width),int(self.mouse_rectangle[0][Y]*self.height)), \
                                         (int(self.mouse_rectangle[1][X]*self.width),int(self.mouse_rectangle[1][Y]*self.height)), \
                                          thickness = 1, color = (0,255,255))

                self.editText('prev press', digit)
                
                self.drawText(image, color = (0,0,255))
                cv2.imshow(IMAGE_NAME, image)
                cv2.imshow(IMAGE_NAME+'2', threshold)
                cv2.imshow('SAMPLE', sample)

                # key event
                key = cv2.waitKey(1)
                if key == 27: break # esc
                elif key == 13: # enter
                    current_selection += 1
                    if current_selection >= len(sample_area): current_selection = -1
                elif key == 32: # space
                    current_selection = -1
                elif key == 8: # backspace # delete previous digit
                    current_selection -= 1
                    responses.pop()
                    samples.pop()
                elif 57 >= key >=48: # digits # or (113 >= key >= 97) and english lower leters
                    digit = int(chr(key))
                    current_selection += 1
                    # keep learning sample
                    sample = sample.reshape((1,sample.size))
                    sample = np.float32(sample)
#                    samples = np.append(samples,sample,0)
                    samples.append(sample)
                    # keep lerning responce
                    responses.append(digit)
                    if current_selection >= len(sample_area): current_selection = -1
                elif key >= 0: print 'KEY PRESSED: ' + str(key) + ' - ' + chr(key)
        finally:
            cv2.destroyAllWindows()
            if len(responses) > 0:
                print "Training complete ^-^"
                
                # order lerning results by responces
                order = sorted(zip(responses, samples), key=lambda x:x[0])
                responses, samples = zip(*order)
                
                # convert samples to numpy array
                samples_save = np.empty((0, SYMBOL_SIZE*SYMBOL_SIZE), dtype=np.float32) # 32x32 samples size
                for x in samples: samples_save = np.append(samples_save,x,0)

                # convert responces to numpy array
                responses = np.array(responses, dtype=np.float32)
                responses = responses.reshape((responses.size,1))

#                np.savetxt(CURRENT_DIR + IMAGE_NAME.lower() + 'knsamples.data', samples)
                np.savetxt(CURRENT_DIR + IMAGE_NAME.lower() + 'knsamples.data', samples_save)
                np.savetxt(CURRENT_DIR + IMAGE_NAME.lower() + 'knresponses.data', responses)

if __name__ == "__main__":
    print 'Use left mouse key for select area on image. This area with relative coordinates will be printed on image in "SELECT" tag.\nUse 0-9 keys (not numpad) to add responce for current selected area (area will be saved as sample).\nResponces and samples will be saved to script directory after exit via Esc key.\nKeys: \nESC - exit. \nSpaceBar - skip image (no save as sample). \n0-9 - digit on slected area (responce for recognition). \nBackspace - delete previuos responce (remove previous sample). \nEnter - skip selected area (no save as sample).'
    sys.stdout.flush()
    CVBasemarkX().main()