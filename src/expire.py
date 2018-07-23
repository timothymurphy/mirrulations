import redis
from redis_manager import RedisManager
import time
import logging

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='expire.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': 'EXPIRE'}
logger = logging.getLogger('tcpserver')

r = RedisManager(redis.Redis())


def expire():
    while(True):
        logger.warning('Awake: %s', 'expire: expire is active', extra=d)
        logger.warning('Calling Function: %s', 'expire: attempting to find expired', extra=d)
        r.find_expired()
        logger.warning('Function Successful: %s', 'expire: find expired successfully', extra=d)
        logger.warning('Sleep: %s', 'expire: sleep for 1 hours', extra=d)
        time.sleep(3600)




