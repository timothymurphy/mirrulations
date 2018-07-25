import json
import logging

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='client.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': 'CONFIG'}
logger = logging.getLogger('tcpserver')

def read_value(value):
    m = json.loads(open("../config.json","r").read())
    try:
        result = m[value]
    except KeyError:
        logger.warning('Exception: %s', 'config: Caught KeyError, no value present for: ' + str(value) + '. Returning None.', extra=d)
        return None
    return result