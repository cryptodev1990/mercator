import os

import logging
import sys

import json_log_formatter

JSON_LOGGING_APP_ENVS = set(["production", "staging"])

def get_logger(name):
    logger = logging.getLogger(name)
    formatter = json_log_formatter.JSONFormatter()
    # add json logger if in prod or staging
    if os.getenv('APP_ENV') in JSON_LOGGING_APP_ENVS:
        print(f"Starting JSON logger: {name}")
        json_handler = logging.FileHandler(filename='/var/log/app.log')
        json_handler.setFormatter(formatter)
        logger.addHandler(json_handler)
    # add stdout logger
    print(f"Starting stdout logger: {name}")
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.INFO)
    return logger
