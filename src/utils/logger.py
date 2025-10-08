import logging
import sys
import os
from datetime import datetime


def setup_print_logger(codigo_etl, log_name="default_logger", log_level=logging.INFO):

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    log_dir = os.path.join(base_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{log_name}_{codigo_etl}_{fecha}.log")
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)  
        ]
    )

    class StreamToLogger:
        def __init__(self, logger, level=logging.INFO):
            self.logger = logger
            self.level = level

        def write(self, message):
            if message.strip():
                self.logger.log(self.level, message.strip())

        def flush(self):
            pass 

    sys.stdout = StreamToLogger(logging.getLogger(log_name))