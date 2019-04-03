from configparser import ConfigParser
from mirrulations_core.mirrulations_logging import logger
import os


def read_value(value):
    """
    Reads a file from the configuration JSON file.
    :param value: Value to be read from the JSON
    :return: Value read from the JSON
    """
    try:
        config = ConfigParser()
        config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                 '../../.config/config.ini'))
        result = config['CONFIG'][value]
    except FileNotFoundError:
        logger.error('File Not Found Error')
        return None
    except IOError:
        logger.error('Input/Output Error')
        return None
    except KeyError:
        logger.error('Key Error')
        return None
    else:
        return result
