import redis
from mirrulations.redis_manager import RedisManager
import time
import logging

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='expire.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': 'EXPIRE'}
logger = logging.getLogger('tcpserver')

r = RedisManager(redis.Redis())


def expire():
    """
    Checks to see if any of the in-progress jobs have expired
    :return:
    """
    while(True):
        r.find_expired()
        time.sleep(3600)


if __name__ == '__main__':
    expire()
