# Module : logger.py
# Purpose : configurator for log operations

import logging
from logging.handlers import RotatingFileHandler
import os

# Directory logs
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Log file
LOG_FILE = os.path.join(LOG_DIR, "ai_operations.log")

# Rotation config (max 1MB, 5 files)
handler = RotatingFileHandler(LOG_FILE, maxBytes=1000000, backupCount=5)

# Standard corporate format
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
handler.setFormatter(formatter)

# AI logger
ai_logger = logging.getLogger("ai_suggestion")
ai_logger.setLevel(logging.DEBUG)
handler.setLevel(logging.DEBUG)
ai_logger.addHandler(handler)
ai_logger.propagate = False