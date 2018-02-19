
from drawpi.runner import main, setup_logging
import logging
import sys

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger()
    if len(sys.argv) < 2:
        logger.error("Must specify command file.")
    else:
        with open(sys.argv[1], 'r') as f:
            text = f.read()
        main(text)