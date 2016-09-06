#!/usr/bin/env python
"""
logger setup
"""
import sys
import logging


_LOGGERS = {
    'LOGGER': None,
    'FILE_HANDLER': None,
    'STDOUT_HANDLER': None
}


STDOUT_FORMATTER = logging.Formatter(
    "%(asctime)s;%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

FILE_FORMATTER = logging.Formatter(
    "%(asctime)s;%(levelname)s;%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)


def get_logger(logfile=None, stdout=True):
    if _LOGGERS['LOGGER']:
        return _LOGGERS['LOGGER']

    log = logging.getLogger('vassal_deployer')
    log.setLevel(logging.DEBUG)
    if stdout and (_LOGGERS['STDOUT_HANDLER'] is None):
        so_handler = logging.StreamHandler(stream=sys.stdout)
        so_handler.setLevel(logging.DEBUG)
        so_handler.setFormatter(STDOUT_FORMATTER)
        _LOGGERS['STDOUT_HANDLER'] = so_handler
        if so_handler not in log.handlers:
            log.addHandler(so_handler)

    if logfile and (_LOGGERS['FILE_HANDLER'] is None):
        handler = logging.handlers.WatchedFileHandler(logfile)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(FILE_FORMATTER)
        _LOGGERS['FILE_HANDLER'] = handler
        if handler not in log.handlers:
            log.addHandler(handler)

    _LOGGERS['LOGGER'] = log
    return _LOGGERS['LOGGER']
