import logging

class Logger:
    def setLogger(log_level,log_file):
        logger = logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
            ])
        return logger
