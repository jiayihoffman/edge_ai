import json
import logging.config
import os
import sys
from os.path import join as pjoin

CONFIG_DIR = 'config'
STD_OUT_PATH_KEY = 'std.out.filename'
_OUT_FILE_OBJ = None

logger = logging.getLogger(__name__)

def setup_logging(default_log_config='robot_car_logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
    ''' Setup logging configuration '''
    path = pjoin(CONFIG_DIR, default_log_config)
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
        if STD_OUT_PATH_KEY in config.keys():
            global _OUT_FILE_OBJ
            _OUT_FILE_OBJ = open(config[STD_OUT_PATH_KEY], 'a', 1)
            sys.stdout = _OUT_FILE_OBJ
            sys.stderr = _OUT_FILE_OBJ
    else:
        print('do not find the log configuration file. use the default configuration.')
        logging.basicConfig(level=default_level)


def close_std_out_file():
    try:
        if _OUT_FILE_OBJ:
            if not _OUT_FILE_OBJ.closed:
                _OUT_FILE_OBJ.close()
                logger.info('Closed Out file')
    except BaseException as e:
        logger.error('Failed to close standard out file. Error: %s', str(e), exc_info=1)
        pass
