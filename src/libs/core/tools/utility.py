# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "12/14/2017 5:21 PM"

import time
from .config import SECOND_CONVERT_FORMAT


class Utility:
    """ Some utils """

    @staticmethod
    def seconds_to_time_format(seconds=0) -> str:
        """
        Convert seconds to time format specified in local config in SECOND_CONVERT_FORMAT variable

        Args:
             seconds (int): Convert seconds to tome format specified in tools.config

        Returns:
            str: Seconds in time format
        """
        return time.strftime(SECOND_CONVERT_FORMAT, time.gmtime(seconds))

    @staticmethod
    def error_to_message(err) -> str:
        """
        Convert catch error to readable message

        Args:
             err (Exception): error

        Returns:
            str error message
        """
        return '%s: %s' % (err.__class__.__name__, err.value.strip('\'').strip('"')
                           if hasattr(err, 'value') else str(err))

    @staticmethod
    def print_error(err, logger=None):
        """
        Print error with logger

        Args:
             err (Exception): error
             logger (logging): Logger to print
        """
        if logger is None:
            from libs.core.logger import getLogger
            logger = getLogger(__file__)

        msg = Utility.error_to_message(err)
        for x in [x for x in msg.split('\n') if x.strip() != '']:
            logger.error('%s' % x)