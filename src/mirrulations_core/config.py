import json
from mirrulations_core.mirrulations_logging import logger
import os


def read_value(value):
    """
    Reads a file from the configuration JSON file.
    :param value: Value to be read from the JSON
    :return: Value read from the JSON
    """
    try:
        configurationpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../config.json")
        contents = json.loads(open(configurationpath, "r").read())
        result = contents[value]
    except FileNotFoundError:
        logger.error('Error - File Not Found')
        return None
    except IOError:
        logger.error('Error - Invalid Input/Output')
        return None
    except json.JSONDecodeError:
        logger.error('Error - Unable to Decode JSON')
        return None
    except KeyError:
        logger.error('API Key Error')
        return None
    else:
        return result
