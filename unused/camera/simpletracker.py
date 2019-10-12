# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "$Nov 27, 2017 11:27:00 PM$"

from Queue import Queue
from libs.logger import logger
from simpletrackerthread import SimpleTrackerThread


class SimpleTracker(object):
    def __init__(self, device=0, settings = None, interval=None, path=None, folder='camera'):
        """
        Args: 
            device (int, default: 0): Camera number
            settings (dict): Camera settings
            interval (int): Make snapshots via time interval in seconds. Disabled if None
            path (str): full path to folder to save camera snaphots
            folder (str): folder name in log folder if path is None
        """
        raise NotImplementedError, 'Feature is not implemented'
        
        # logger
        self.logger = logger.getLogger(__file__)
        # tasks
        self.task_queue = Queue()
        self.tracker = SimpleTrackerThread(self.task_queue, device, settings, interval, path, folder)

    def startCamera(self):
        """ start camera process """
        self.tracker.daemon = True
        self.tracker.start()
#        self.tracker.join()
    
    def takeScreenshot(self, name=None):
        """ make screenshot """
        if self.tracker is not None and self.tracker.is_alive():
#            self.tracker.task_queue = 'screenshot:%s' % name
            self.task_queue.put('screenshot:%s' % name)
        else: 
            raise Exception, 'Camera process is not alive !'
    
    def releaseCamera(self):
        """ release camera after use """
        self.task_queue.put('exit')
#        self.tracker.task_queue = 'exit'
        self.logger.info('Wait for exit camera process...')
        if self.tracker is not None and self.tracker.is_alive():
            self.tracker.join()
        self.logger.info('Done.')
            