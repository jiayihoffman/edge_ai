import datetime
import logging
import os


def init_logging():
    log_path = os.path.dirname(__file__) + '/../logs'
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    today = datetime.datetime.now().strftime("%m-%d-%y")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(f"{log_path}/audio_video_{today}.log"),
            logging.StreamHandler()
        ]
    )