import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime


def create_log_file(log_file_name):
    current_date = datetime.now().strftime('%Y-%m-%d')
    LOG_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..","..","..",'Logs',current_date)
    )
    os.makedirs(LOG_DIR, exist_ok=True)
   
    LOG_FILE = os.path.join(LOG_DIR, log_file_name+"_"+str(datetime.now().strftime('%Y-%m-%d %H_%M_%S'))+".log")
    return LOG_FILE



def setup_logging(log_file_name):
    level=logging.INFO
    logger = logging.getLogger()
    logger.setLevel(level)

    # Prevent duplicate logs
    if logger.handlers:
        return

    LOG_FORMAT = (
    "%(asctime)s | "
    " %(filename)s:%(lineno)d | %(message)s"
    )
    formatter = logging.Formatter(LOG_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File handler (rotating)
    file_handler = RotatingFileHandler(
        create_log_file(log_file_name), maxBytes=5_000_000, backupCount=5
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
