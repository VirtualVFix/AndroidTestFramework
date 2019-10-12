# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "12/31/2017 1:38 PM"

import sys
import asyncio
from libs.core.template import NAME
from libs.core.logger import getSysLogger


class Async:
    """ Async help tools """

    @staticmethod
    def get_event_loop(win32=False):
        """
        Return current event loop or create new if loop closed.

        Args:
            win32 (bool): Return ProactorEventLoop if available
                          (Proactor event loop for Windows using “I/O Completion Ports”)

        Returns:
             EventLoop
        """
        if win32 is True and sys.platform == 'win32':
            event_loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(event_loop)
        else:
            event_loop = asyncio.get_event_loop()
            if event_loop.is_closed():
                asyncio.set_event_loop(asyncio.new_event_loop())
                event_loop = asyncio.get_event_loop()

        return event_loop

    @staticmethod
    def add_error_handler(loop=None):
        """
        Add error handler to event loop

        Args:
            loop (EventLoop) Current event loop
        """
        # logger
        syslogger = getSysLogger()

        event_loop = loop if loop is not None else asyncio.get_event_loop()
        if event_loop.is_closed():
            syslogger.info('Event loop already closed !')
            return

        # add empty exception handler
        def exception_handler(loop, context):
            logger = getSysLogger()
            logger.exception(context["exception"] if 'exception' in context else 'async error: %s ' % context)

        event_loop.set_exception_handler(exception_handler)

    @staticmethod
    def close_loop(loop=None):
        """
        Close all not finished tasks and close event loop

        Args:
            loop (EventLoop) Current event loop to close
        """
        # logger
        syslogger = getSysLogger()

        event_loop = loop if loop is not None else asyncio.get_event_loop()
        if event_loop.is_closed():
            syslogger.info('Event loop already closed !')
            return

        # cancel all tasks whatever is it finished or not
        tsk = asyncio.Task.all_tasks(loop=loop)
        syslogger.info('Coroutine count: %d' % len(tsk))
        for x in tsk:
            syslogger.info('Coroutine %s is %s' % (NAME.safe_substitute(name=x), x._state))

        # cancel all tasks it it not completed
        tasks = asyncio.gather(*asyncio.Task.all_tasks(loop=event_loop), loop=event_loop, return_exceptions=True)
        tasks.add_done_callback(lambda t: event_loop.stop())
        tasks.cancel()

        # wait for tasks cancellation
        while not tasks.done() and not event_loop.is_closed():
            event_loop.run_forever()

        event_loop.close()
