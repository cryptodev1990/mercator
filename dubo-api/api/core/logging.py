import os

import logging
import sys

import json_log_formatter


def get_logger(name):
    logger = logging.getLogger(name)
    formatter = json_log_formatter.JSONFormatter()
    if os.getenv('APP_ENV') == 'production':
        json_handler = logging.FileHandler(filename='/var/log/app.log')
        json_handler.setFormatter(formatter)
        logger.addHandler(json_handler)
    else:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)
    return logger
