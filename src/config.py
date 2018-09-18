import json
import logging

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
    logger.warning('Calling Function: %s', 'read_value: Reading a value from the configuration file', extra=d)
    try:
        logger.warning("Assign Variable: %s", 'read_value: loading json from config', extra=d)
        contents = json.loads(open("./config.json","r").read())
        logger.warning("Variable Success: %s", 'read_value: found json from config', extra=d)
    except:
        logger.warning('Exception: %s', 'read_value: Error opening/loading JSON', extra=d)

    try:
        result = contents[value]
    except KeyError:
        logger.warning('Exception: %s', 'config: Caught KeyError, no value present for: ' + str(value) + '. Returning None.', extra=d)
        return None
    return result
