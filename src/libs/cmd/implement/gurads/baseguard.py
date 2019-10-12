# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "15/03/18 21:10"

import re
from time import sleep
from config import CONFIG
from functools import wraps
from libs.core.logger import getLoggers
from ..constants import CMD_SWITCH_RECONNECT_DELAY, CMD_RETRY_DELAY
from ..exceptions import DeviceEnumeratedError, TimeoutExpiredError, AdbInternalError, MoreOneDeviceError
from ..constants import CMD_RETRY_AFTER_TIMEOUT_ERROR, CMD_SWITCH_RECONNECT_AFTER, CMD_RETRY_COUNT


def BaseGuard(func):
    """
    Base commands implementation execute guard.
    May restart command according to options.
    Also may reconnect switchboard according to options.

    Keyword args:
        retry_count (int, default :data:`.constants.CMD_RETRY_COUNT`): Command retry counter. Allow retry when > 0
        switch_reconnect_after (int, default :data:`.constants.CMD_SWITCH_RECONNECT_AFTER`): Switch board reconnect
            after each N retry. Allow switch reconnect when > 0. Should be <= CMD_RETRY_COUNT
        allow_timeout_retry (bool, default :data:`.constants.CMD_RETRY_AFTER_TIMEOUT_ERROR`):
            Allow retry after TimeoutExpired error
        switch_reconnect_delay (int, default :data:`.constants.CMD_SWITCH_RECONNECT_DELAY`):
            Switch reconnect delay in seconds
        retry_delay (int, default :data:`.constants.CMD_RETRY_DELAY`): Retry delay in seconds
    """

    logger, syslogger = getLoggers(__file__)

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            # Allow retry after TimeoutExpired error
            allow_timeout_retry = kwargs.get('allow_timeout_retry', CMD_RETRY_AFTER_TIMEOUT_ERROR)
            # command retry
            retry_count = kwargs.get('retry_count', CMD_RETRY_COUNT)
            # total retry counter
            retry_count_total = kwargs.get('__retry_count_total__', retry_count)
            # retry delay
            retry_delay = kwargs.get('retry_delay', CMD_RETRY_DELAY)
            # switch reconnect
            switch_reconnect_after = kwargs.get('switch_reconnect_after', CMD_SWITCH_RECONNECT_AFTER)
            # fix when it switch_each > retry_count
            if switch_reconnect_after > 0 and switch_reconnect_after > retry_count_total:
                switch_each = retry_count_total
            # switch reconnect delay
            switch_delay = kwargs.get('switch_reconnect_delay', CMD_SWITCH_RECONNECT_DELAY)
            try:
                out = func(self, *args, **kwargs)

                # check multiply device error
                error = re.search('\s*error[\s:]+more than one device.*', out, re.I | re.M | re.DOTALL)
                if error:
                    raise MoreOneDeviceError(out.strip())

                # device offline
                error = re.search('\s*error[\s:]+device offline.*', out, re.I | re.M | re.DOTALL)
                if error:
                    raise DeviceEnumeratedError(out.strip())

                # device not found
                error = re.search('\s*error[\s:]+device[\s\w\'"]+not found.*', out, re.I | re.M | re.DOTALL)
                if error:
                    raise DeviceEnumeratedError(out.strip())

                # protocol fault
                error = re.search('\s*error[\s:]+protocol fault.*', out, re.I | re.M | re.DOTALL)
                if error:
                    raise AdbInternalError(out.strip())

                # android exception
                error = re.search('androidexception:(.*)', out.replace('\n', ' '), re.I | re.M | re.DOTALL)
                if error:
                    raise AdbInternalError(out.strip())
            except (AdbInternalError, DeviceEnumeratedError, TimeoutExpiredError) as e:
                if isinstance(e, TimeoutExpiredError) and allow_timeout_retry is False:
                    raise e.__class__(e)
                if retry_count <= 0:
                    raise e.__class__(e)

                # retry command
                logger.warning('Retrying [%s] command due to [%s(%s)]. Remaining attempts: %d'
                               % (self.command.lastcommand, e.__class__.__name__, e, retry_count-1))
                syslogger.exception(logger.lastmsg)

                # switch reconnect
                if switch_reconnect_after > 0 and (retry_count_total - retry_count + 1) % switch_reconnect_after == 0:
                    if CONFIG.SWITCH.CLASS is not None:
                        try:
                            # logger.warning('Try to reconnect Switchboard port...')
                            logger.warnlist('USB reconnection due to [%s] error !' % e)
                            switch = CONFIG.SWITCH.CLASS(CONFIG.SWITCH.SERIAL)
                            switch.disconnect()
                            sleep(switch_delay)
                            switch.connect()
                            sleep(switch_delay)
                            logger.done()
                        except Exception as e:
                            syslogger.exception(e)
                else:
                    if retry_delay > 0:
                        logger.info('%s seconds retry delay...' % retry_delay)
                        sleep(retry_delay)
                kwargs['retry_count'] = retry_count-1
                kwargs['__retry_count_total__'] = retry_count_total
                return wrapper(self, *args, **kwargs)
            return out
        except:
            raise
    return wrapper
