# All rights reserved by forest fairy.
# You cannot modify or share anything without sacrifice.
# If you don't agree, keep calm and don't look at code bellow!

"""
Additional functions integrated to `logging.Logger` class when new logger created in :mod:`src.libs.core.logger` module.
"""

__author__ = "VirtualV <https://github.com/virtualvfix>"
__date__ = "07/10/17 20:03"

import copy
import logging
from .config import LOCAL
from .exceptions import TableFormatError, TableSizeError, TableError


def table(self, *args, level=logging.INFO, border_delimiter=None, column_delimiter=None):
    """
    Print one table row according to format specified as function parameters.

    Args:
        *args (tuple, list or str): Table map - (`MSG`, `PERCENTAGE`, `ALIGN`)
            or [MSG`, `PERCENTAGE`, `ALIGN`] or MSG
        *args (logging.Logger): Additional loggers to spam
        level (int): Logger level
        border_delimiter (str): Border delimiter symbols
        column_delimiter (str): Columns delimiter symbols

    Note:
        - `MSG` (str): Required, but can be empty. `MSG` ends with `*` fill whole column to ``MSG`` message.
        - `ALIGN` (str, optional, Default: left): Allow commands - `L` or `left`, `C` or `center` or `R` or `right`.
        - `PERCENTAGE` (int, optional): Size in percentage of console width.
            Should be <= 100 and > 0 in sum of all columns. Column size will be calculated automatically if
            `PERCENTAGE` not set or equal 0.

    Raises:
        TableSizeError: Table column size error.
        TableFormatError: Error in table map.
        TableError: Any other exception.

    Note:
        Raises are allowed in debug framework mode and when logger or table level is <= logging.DEBUG.
        Otherwise error is logged and dont interrupt main process.

    Example:

    .. code-block:: python

        # print table with 2 column with 50% console width each
        self.logger.table(('message', 50, 'L'), ('message 2', 50), self.syslogger)
        > |message             |       message 2       |

        # the same result
        self.logger.table(('message', 'L'), ('message 2'), self.syslogger)
        > |message             |       message 2       |

        # fill whole column with '=' message. Analog: '='*column_size
        self.logger.table('=*')
        > +===========================================+

        # print table
        self.logger.table('=*')
        self.logger.table(('Test', 60, 'C'), ('Description', 'C'))
        self.logger.table('-*')
        self.logger.table(('test 01', 60, 'C'), ('test 01 description', 'C'))
        self.logger.table(('test 02', 60, 'C'), 'test 02 desc')
        self.logger.table(('test 03', 60, 'C'), ('test 03 desc', 'R'))
        self.logger.table('=*')

        > +==========================================+
        > |            Test           | Description  |
        > +------------------------------------------+
        > |           test 01         |   test 01    |
        > |                           | description  |
        > |           test 02         |test 02 desc  |
        > |           test 03         |  test 03 desc|
        > +==========================================+
    """
    # delimiter symbols
    border_delimiter = str(border_delimiter) if border_delimiter is not None else LOCAL.TABLE_BORDER_DELIMITER
    column_delimiter = str(column_delimiter) if column_delimiter is not None else LOCAL.TABLE_COLUMNS_DELIMITER

    # all available loggers
    loggers = None
    loggers = [x for x in args if isinstance(x, logging.Logger)]
    loggers.insert(0, self)

    def error(cls, err):
        """
        Raise error if logger or framework in debug mode otherwise just logged error
        """
        if LOCAL.DEBUG or level <= logging.DEBUG or self.level <= logging.DEBUG:
            raise cls(err)
        else:
            # print error if non debug mode framework or logger mode
            for _log in loggers:
                _log._log(logging.ERROR, 'Table error: %s %s' % (err, ' <Use debug mode to get traceback>'), None)

    # get table map arguments
    table_map = [x for x in args if isinstance(x, (int, float, str, tuple, list))]
    if len(table_map) == 0:
        error(TableFormatError, 'Table format is not specified ! Expected format: '
                                + '(`MSG`, `PERCENTAGE`, `ALIGN`) or [MSG`, `PERCENTAGE`, `ALIGN`] or MSG')
        return

    # prepare table map
    tmp = []
    for i, x in enumerate(table_map):
        # get message
        msg = str(x[0]) if isinstance(x, (tuple, list)) else str(x) if isinstance(x, (int, float, str)) else None
        if msg is None:
            error(TableFormatError, 'Message not found for "%d" column !' % (i+1))
            msg = ' '  # fix error in non debug mode

        # get size
        size = int(x[1]) if isinstance(x, (tuple, list)) and len(x) > 1 and isinstance(x[1], (int, float)) else -1
        size_ind = 1 if size != -1 else 0
        # get align
        align = x[size_ind + 1].lower() if isinstance(x, (tuple, list)) and len(x) > size_ind + 1 \
                                           and isinstance(x[size_ind + 1], str) else LOCAL.TABLE_DEFAULT_ALIGN.lower()
        tmp.append({'msg': msg, 'size': size if size != -1 else 0, 'align': align, 'rows': 1})
        del size, msg, align

    # calculate column sizes
    total = sum((x['size'] for x in tmp))
    if total > 100:
        error(TableSizeError, 'Summary of columns size should be <= 100')
        # fix error in non debug mode
        for x in tmp:
            x['size'] = int(100 / len(tmp))
        total = int(100/len(tmp)) * len(tmp)

    empty = sum((1 for x in tmp if x['size'] == 0))
    if empty + total > 100:
        error(TableSizeError, 'Some columns not enough space to draw')
        # fix error in non debug mode
        for x in tmp:
            x['size'] = 100 / len(tmp)

    try:
        # calc size for columns without size
        nosize = [i for i, y in enumerate((x for x in tmp)) if y['size'] == 0]
        for i in nosize:
            tmp[i]['size'] = int((100-total) / empty)

        # lost percents due to integer divide
        lost = 100 - (total + int((100-total) / empty) * empty) if empty > 0 else 0
        # evenly distributes lost percentage
        while lost > 0:
            for i in reversed(nosize):
                if lost <= 0:
                    break
                tmp[i]['size'] += 1
                lost -= 1

        # prepared table map
        table_map = tmp

        del tmp, lost, nosize, empty, total

        # replace handle function to keep handler record
        def newhandler(self, record):
            self.stored_record = record

        # spam to all loggers
        for log in loggers:
            # replace handle function
            for hdlr in log.handlers:
                hdlr.original_handle = hdlr.handle
                hdlr.handle = lambda x, self=hdlr: newhandler(self, x)

            # create record
            log._log(level, '', None)

            # print table to all handlers
            for hdlr in log.handlers:
                # restore handle function
                hdlr.handle = hdlr.original_handle
                # remove additional attributes
                delattr(hdlr, 'original_handle')

                # logger prefix size
                hdlr.stored_record.__dict__['msg'] = ''
                logger_offset = len(hdlr.format(hdlr.stored_record))
                # increase table size for file logger
                if isinstance(hdlr, logging.FileHandler):
                    logger_offset = int(logger_offset/LOCAL.DEFAULT_FILE_LOGGER_OFFSET_DENOMINATOR)

                # copy map due to map will be modified
                local_map = copy.deepcopy(table_map)

                # calc real columns size
                for tmap in local_map:
                    tmap['size'] = int((LOCAL.CONSOLE_WIDTH - len(column_delimiter) - logger_offset)
                                       * (tmap['size']/100)) - len(column_delimiter)

                # lost spaces due to calc percentage of each column
                lost = LOCAL.CONSOLE_WIDTH - len(column_delimiter) * len(local_map) - logger_offset \
                       - sum((x['size'] for x in local_map))
                # evenly distributes lost spaces
                while lost > 0:
                    for tmap in reversed(local_map):
                        if lost <= 0:
                            break
                        tmap['size'] += 1
                        lost -= 1

                # row cycle. message in column may need more one row
                row = 1
                while row > 0:
                    out = ''
                    for i, tmap in enumerate(local_map):
                        # get message
                        msg = tmap['msg'].strip()
                        # cut long message by space or by column size
                        if len(msg) > tmap['size']:
                            tmap['rows'] += 1
                            tmp = ''
                            for k, x in enumerate(msg.split()):
                                if len(tmp + x) < tmap['size']:
                                    if k > 0:
                                        tmp += ' '
                                    tmp += x
                                else:
                                    break
                            tmap['msg'] = ' '.join(msg.split())
                            msg = tmp
                            # cut by column size
                            if len(msg) == 0:
                                msg = tmap['msg'][:tmap['size']]
                        tmap['msg'] = tmap['msg'][len(msg):]

                        # fill whole column row
                        if msg.endswith('*'):
                            msg = msg[:-1]
                            # add begin delimiter
                            if out.startswith(column_delimiter):
                                out += column_delimiter
                            else:
                                out += border_delimiter

                            if msg == '':  # fix empty message
                                msg = ' '
                            tmp = msg * int(tmap['size']/len(msg) + 1)
                            tmp = tmp[:tmap['size']]
                            out += tmp

                            # add end delimiter
                            if i == len(local_map) - 1:
                                if out.startswith(column_delimiter):
                                    out += column_delimiter
                                else:
                                    out += border_delimiter
                        else:  # regular row
                            # add begin delimiter
                            if out.startswith(border_delimiter):
                                out += border_delimiter
                            else:
                                out += column_delimiter

                            # align text in column
                            # left align
                            if tmap['align'].startswith('l'):
                                out += msg + ' '*(tmap['size'] - len(msg))
                            # right align
                            elif tmap['align'].startswith('r'):
                                out += ' ' * (tmap['size']-len(msg)) + msg
                            # center align
                            else:
                                out += ' ' * int((tmap['size']-len(msg)) / 2)
                                out += msg
                                out += ' ' * (tmap['size'] - len(msg) - int((tmap['size']-len(msg)) / 2))

                            # add end delimiter
                            if i == len(local_map) - 1:
                                if out.startswith(border_delimiter):
                                    out += border_delimiter
                                else:
                                    out += column_delimiter

                    # print table in current handler
                    hdlr.stored_record.__dict__['msg'] = out
                    hdlr.handle(hdlr.stored_record)

                    # row was draw
                    for tmap in local_map:
                        tmap['rows'] -= 1

                    # calc current row
                    row = max((x['rows'] if x['rows'] > 0 else 0 for x in local_map))

                # remove additional attributes
                delattr(hdlr, 'stored_record')
    except Exception as e:
        # restore handles
        if loggers is None:
            loggers = [self]
        for log in loggers:
            for hdlr in log.handlers:
                if hasattr(hdlr, 'stored_record'):
                    delattr(hdlr, 'stored_record')
                if hasattr(hdlr, 'original_handle'):
                    hdlr.handle = hdlr.original_handle
                    delattr(hdlr, 'original_handle')

        error(TableError, 'Table build error: %s' % e)
