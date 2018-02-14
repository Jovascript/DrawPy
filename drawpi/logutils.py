'''Utils to help logging, cos theres no better way...'''
import logging
log_settings_complete = False
def prepare_logger(name)->logging.Logger:
    """Setup logger"""
    global log_settings_complete
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
    log_settings_complete = True
    return log

def get_logger(name):
    global log_settings_complete
    if log_settings_complete:
        return logging.getLogger(name)
    else:
        return prepare_logger(name)
