import redis
from redis_manager import RedisManager
import time

r = RedisManager(redis.Redis())

def expire():
    while(True):
        r.find_expired()
        time.sleep(3600)




