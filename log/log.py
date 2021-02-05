import logging

NO_LOG  = 0
ERROR   = 1
WARNING = 2
INFO    = 3
DEBUG   = 4

logger = None


def log_init(level):

    global logger

    logger  = logging.getLogger()
    handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s.%(msecs)03d - %(levelname)-7s - %(message)s', '%H:%M:%S')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    if level is None:

        logger.setLevel(logging.DEBUG)

    else:

        log_set_level(level)


def log_set_level(level):

    if level == NO_LOG:
        logger.debug('Logs disabled')
        logger.setLevel(logging.CRITICAL)
    elif level == ERROR:
        logger.debug('Log level set to ERROR')
        logger.setLevel(logging.ERROR)
    elif level == WARNING:
        logger.debug('Log level set to WARNING')
        logger.setLevel(logging.WARNING)
    elif level == INFO:
        logger.debug('Log level set to INFO')
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)
        logger.debug('Log level set to DEBUG')


def log(level, message):

    global logger

    if level == DEBUG:
        logger.debug  (message)
    elif level == WARNING:
        logger.warning(message)
    elif level == INFO:
        logger.info   (message)
    else:
        logger.error  (message)
