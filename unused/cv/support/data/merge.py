# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$May 19, 2016 4:21:36 PM$"

import os
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__)) + os.sep
SAMPLE_SIZE = 32

def concatenate():
    responses = []
    samples = []
    for dirs,subs,files in os.walk(CURRENT_DIR):
        for file in files:
            if 'responses' in file.lower() and not file.startswith('kn'):
#                print file, len(np.loadtxt(CURRENT_DIR + file, np.float32)), len(np.loadtxt(CURRENT_DIR + file.replace('responses','samples'), np.float32))
                for x in np.loadtxt(CURRENT_DIR + file, np.float32):
                    responses.append(x)
                for x in np.loadtxt(CURRENT_DIR + file.replace('responses','samples'), np.float32):
                    samples.append(x)

    print len(responses), len(samples)
    # sort lerning results by responces
    order = sorted(zip(responses, samples), key=lambda x:x[0])
    responses, samples = zip(*order)

    # convert samples to numpy array
    samples = np.array(samples, dtype=np.float32)

    # convert responces to numpy array
    responses = np.array(responses, dtype=np.float32)
    responses = responses.reshape((responses.size,1))

    # save all data
    np.savetxt(CURRENT_DIR + 'knsamples.data', samples)
    np.savetxt(CURRENT_DIR + 'knresponses.data', responses)
    
    print 'Complete !'
    
if __name__ == "__main__":
    concatenate()
    
