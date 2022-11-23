import logging
import sys

import json_log_formatter

def get_logger(name):
    formatter = json_log_formatter.JSONFormatter()
    json_handler = logging.StreamHandler(stream=sys.stdout)
    json_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(json_handler)
    logger.setLevel(logging.INFO)
    return logger
