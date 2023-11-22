import logging

def get_logger() -> logging.RootLogger:
    logger = logging.getLogger()
    return logger