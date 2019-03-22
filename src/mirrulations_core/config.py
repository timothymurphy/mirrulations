import json
import logging
import os

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='client.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': 'CONFIG'}
logger = logging.getLogger('tcpserver')


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
        logger.error('File Not Found Error')
        return None
    except IOError:
        logger.error('Input/Output Error')
        return None
    except json.JSONDecodeError:
        logger.error('JSON Decode Error')
        return None
    except KeyError:
        logger.error('Key Error')
        return None
    else:
        return result
