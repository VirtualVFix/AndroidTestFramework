# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "12/5/2017 10:28 AM"

from libs.core.logger import getSysLogger


class DataBase:
    """ Connect to data base and prepare DB """

    def __init__(self):
        pass

    @staticmethod
    async def connect():
        """
        Connect to DB according to config file
        """
        syslogger = getSysLogger()
        syslogger.warning('DATA BASE NOT IMPLEMENTED YET ! CONNECTION FAILED !')
