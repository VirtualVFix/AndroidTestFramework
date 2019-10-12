# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$May 6, 2016 4:51:32 PM$"

import os
import cv2
import numpy as np
from config import CONFIG
import libs.logger as logger

DATA_DIR = os.path.dirname(os.path.realpath(__file__)) + os.sep + 'data' + os.sep
WIDTH,HEIGHT=1,0
X,Y=0,1

class CV(object):
    """ main class for digit recognition """
    def __init__(self):#, bench_name):
        self.DEBUG = False
        self.DEBUG_DATA = {}
#        self.IMAGE_NAME = bench_name
        self.IMAGE_SCALE = 1 # scale parameter
        self.CROP_AREA = [(0,0), (1, 1)] # relative rectangle coordinates for crop image
        self.__SAMPLE_SIZE = 32
        self.__digit_model = cv2.KNearest()
        self.logger = logger.getLogger(__file__) # main logger
        self.sys_logger = logger.getLogger('sys', 'sys.log', propagate=False) # sys logger
        
#        if not os.path.exists(DATA_DIR + bench_name.lower() + 'knsamples.data'): raise 'CV "knsamples.data" is N/A !'
#        samples = np.loadtxt(DATA_DIR + bench_name.lower() + 'knsamples.data', np.float32)
#        responses = np.loadtxt(DATA_DIR + bench_name.lower() + 'knresponses.data', np.float32)

        if not os.path.exists(DATA_DIR + 'knsamples.data'): raise 'CV "knsamples.data" is N/A !'
        if self.DEBUG: print 'USED {} and {} files'.format(DATA_DIR + 'knsamples.data', DATA_DIR + 'knresponses.data')
        
        samples = np.loadtxt(DATA_DIR + 'knsamples.data', np.float32)
        responses = np.loadtxt(DATA_DIR + 'knresponses.data', np.float32)
        self.__digit_model.train(samples, responses)
        
    def __getBinarySampleByArea(self, threshold, sample_area):
        """ Get image sample, resize it to "self.SAMPLE_SIZE" size and convert to full binary image """
        sample = threshold[sample_area[Y]:sample_area[Y]+sample_area[3],sample_area[X]:sample_area[X]+sample_area[2]]
        sample = cv2.resize(sample, (self.__SAMPLE_SIZE, self.__SAMPLE_SIZE))
        # convert image to read binarry (only 0 or 255 color value)
        for i in xrange(len(sample)): 
            for j in xrange(len(sample[i])):
                if sample[i][j] < 255/2:
                    sample[i][j] = 0
                else: sample[i][j] = 255
        return sample
    
    def step1ScaleImage(self, image):
        """ scale image by self.IMAGE_SCALE parameter. Returns resized image """
        img = np.copy(image)
        # resize image
        if self.IMAGE_SCALE != 1:
            img = cv2.resize(img, (int(img.shape[WIDTH]/self.IMAGE_SCALE), int(img.shape[HEIGHT]/self.IMAGE_SCALE)))
        return img
    
    def step2CropImage(self, image):
        """ Crop image by self.CROP_AREA parameter. Returns cropped image """
        img = np.copy(image)
        # crop image
        return img[int(img.shape[HEIGHT]*self.CROP_AREA[0][Y]):int(img.shape[HEIGHT]*self.CROP_AREA[1][Y]), 
                  int(img.shape[WIDTH]*self.CROP_AREA[0][X]):int(img.shape[WIDTH]*self.CROP_AREA[1][X])]
    
    def step3PrepareImage(self, image):
        """ Prepare image. Returns prepared image """
        raise IndentationError, "Feature is not implemented yet !"
    
    def step4GetDigitArea(self, image):
        """ Get sample area. 
            IN: threshold image
            OUT: List of cv2.boundingRect(SAMPLE_CONTOUR) grouped by line. [[(x,y,w,h), (x,y,w,h)], [(x,y,w,h)], [...]] """
        raise IndentationError, "Feature is not implemented yet !"
    
    def step5GetSamples(self, image, digit_area_list):
        """ Get samples. 
            IN: threashold image 
            OUT: List of samples (np.float32 array) """
        if len(digit_area_list) == 0: raise Exception, 'Digit Area list is N/A !'
        # get samples by areas
        results = []
        for grp in digit_area_list:
            _sample_group = []
            for smpl_area in grp:
                _sample_group.append(self.__getBinarySampleByArea(image, smpl_area))
            results.append(_sample_group)
        return results
    
    def step6RecognizeDigits(self, sample_list, nearest=1):
        """ Recognition digit 0-9 and point by samples. 
            IN: Groups of samples [[sample1, sample2], [sample3, sample4]]
            OUT: List of digits as string: ['123', '123', '123'] """
        results = []
        for grp in sample_list:
            _line = ''
            for smpl in grp:
                _sample = smpl.reshape((1,smpl.size))
                _sample = np.float32(_sample)
                _retval, _results, _neigh_resp, _dists = self.__digit_model.find_nearest(_sample, k=nearest)
                _res = int(_results[0][0])
                if _res == 46: _res = '.' 
                _line += str(_res)
            results.append(_line if _line != '' else -1)
        return results
    
    def _getDigits(self, image):
        """ recognize digits from image """
        if self.DEBUG: self.DEBUG_DATA['original_image'] = np.copy(image)

        # 1. scale image 
        img = self.step1ScaleImage(image)
        if self.DEBUG: self.DEBUG_DATA['scale_image'] = np.copy(img)

        # 2. crop image 
        img = self.step2CropImage(img)
        if self.DEBUG: self.DEBUG_DATA['crop_image'] = np.copy(img)

        # 3. prepare image 
        img = self.step3PrepareImage(img)
        if self.DEBUG: self.DEBUG_DATA['prepare_image'] = np.copy(img)

        # 4. get gigit area
        area_list = self.step4GetDigitArea(img)
        if self.DEBUG: self.DEBUG_DATA['area_group_list'] = area_list

        # 5. get samples 
        sample_list = self.step5GetSamples(img, area_list)
        if self.DEBUG: self.DEBUG_DATA['sample_group_list'] = sample_list

        # 6. recognition digits
        digit_list = self.step6RecognizeDigits(sample_list)
        if self.DEBUG: self.DEBUG_DATA['digit_list'] = digit_list
        
        return digit_list 
    
    def getDigits(self, image_path):
        try:
            image = cv2.imread(image_path)
            digit_list = self._getDigits(image)
            if not self.DEBUG:
                if digit_list is None or len(digit_list) == 0: raise Exception, 'Results are not found !'
            return digit_list
        except Exception, e:
            if CONFIG.DEBUG: self.logger.exception('Results cannot be recognized !' + str(e))
            self.sys_logger.exception('Results cannot be recognized !' + str(e))
            raise Exception, 'Results cannot be recognized ! ' + str(e)
    
#    
#    def _recognition(self, samples, nearest=1):
#        """ recognition digit by sample. Retrun digits as string """
#        string = ''
#        for i in xrange(len(samples)):
#            sample = samples[i].reshape((1,samples[i].size))
#            sample = np.float32(sample)
#            retval, results, neigh_resp, dists = self.__digit_model.find_nearest(sample, k=nearest)
#            d = int(results[0][0])                
#            string += str(d)
#        return string if string != '' else -1
#    
#    def _cropImageByDigitArea(self, image):
#        """ crop image by digit area. Return cropped image """
#        img = np.copy(image)
#        # resize and crop image
#        if self.IMAGE_SCALE != 1: img = cv2.resize(img, (int(img.shape[WIDTH]/self.IMAGE_SCALE), int(img.shape[HEIGHT]/self.IMAGE_SCALE)))
#        img = img[int(img.shape[HEIGHT]*self.digit_area[0][Y]):int(img.shape[HEIGHT]*self.digit_area[1][Y]), 
#                  int(img.shape[WIDTH]*self.digit_area[0][X]):int(img.shape[WIDTH]*self.digit_area[1][X])]
#        return img
#    
#    def _prepareImage(self, image):
#        """ prepare image. Return prepared image """
#        raise IndentationError, 'Feature is not implemented yet !'
#    
#    def _getSampleAreaList(self, image):
#        """ get sample area. return list of cv2.boundingRect(SAMPLE_CONTOUR) """
#        raise IndentationError, 'Feature is not implemented yet !'
#    
#    def _getSamples(self, image, area_list):
#        """ get samples. return list of samples (np.float32 array)"""
#        # get samples by areas
#        recog_smpls = []
#        for i in xrange(len(area_list)):
#            recog_smpls.append(self._getBinarySampleByArea(image, area_list[i])) 
#        return recog_smpls    
#    
#    def getDigit(self, image):
#        crop_image = self._cropImageByDigitArea(image)
#        prepare_image = self._prepareImage(crop_image)
#        sample_area_list = self._getSampleAreaList(prepare_image)
#        samples = self._getSamples(prepare_image, sample_area_list)
#        return self._recognition(samples)
#    
#    def getDigitDebug(self, image):
#        print 'DEBUG "getDigitDebug" function !'
#        self.crop_image = self._cropImageByDigitArea(image)
#        self.prepare_image = self._prepareImage(self.crop_image)
#        self.sample_area_list = self._getSampleAreaList(self.prepare_image)
#        self.samples = self._getSamples(self.prepare_image, self.sample_area_list)
#        return self._recognition(self.samples)
    
    
    
    
