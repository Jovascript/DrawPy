'''Main file for running a command file'''
from drawpi.runner import main, setup_logging
import logging
import sys

if __name__ == "__main__":
    # Setup the logger
    setup_logging()
    logger = logging.getLogger()
    # Check whether file is specified.
    if len(sys.argv) < 2:
        logger.error("Must specify command file.")
    else:
        # Open command file and execute it
        with open(sys.argv[1], 'r') as f:
            text = f.read()
        main(text)