'''DRAWPI(Y)'''
import logging

def prepare_logger(name)->logging.Logger:
    """Setup logger"""
    # create logger with correct name
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    log.addHandler(ch)
    return log

