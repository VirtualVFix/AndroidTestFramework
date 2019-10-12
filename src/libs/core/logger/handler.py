# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "12/21/2017 4:04 PM"

import os
import shutil
import zipfile
from logging.handlers import RotatingFileHandler


class FileHandlerWithCompress(RotatingFileHandler):
    """
    Rotation file logger handler with compress files to zip
    """

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        super(FileHandlerWithCompress, self).__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        self.totalCount = 0

    def doRollover(self):
        """
        Rollover log files and compress it.
        """
        self.totalCount += 1

        if self.stream:
            self.stream.close()
            self.stream = None

        # rename file
        new_name = '%s.%d.log' % (self.baseFilename[:-4], self.totalCount)
        shutil.move(self.baseFilename, new_name)

        # add file to archive
        archive = self.baseFilename + '.zip'
        with zipfile.ZipFile(archive, 'a' if os.path.exists(archive) else 'w') as file:
            file.write(new_name, os.path.split(new_name)[1], zipfile.ZIP_DEFLATED)
        os.remove(new_name)

        if not self.delay:
            self.stream = self._open()
