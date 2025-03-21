import logging
import os


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler("logs/log.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger()
