import json
import logging
import random
import redis
import string
import time
import mirrulations_server.redis_manager as redis_manager
from mirrulations_core.api_call_manager import APICallManager
import mirrulations_core.config as config

key = config.read_value('SERVER', 'key')

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='redis_log.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': 'REDIS'}
logger = logging.getLogger('tcpserver')

r = redis_manager.RedisManager(redis.Redis())
api = APICallManager(key)


def get_max_page_hit(results_per_page):

    try:
        records = api.documents_call(counts_only=True, results_per_page=results_per_page).json
        return records["totalNumRecords"] // results_per_page
    except api.CallFailException:
        logger.error('Error occured with API request')
        print("Error occurred with docs_work_gen regulations API request.")
        exit()


def get_work(results_per_page):

    max_page_hit = get_max_page_hit(results_per_page)

    current_page = 0

    while current_page < max_page_hit:
        docs_info_list = []

        for i in range(results_per_page):
            current_page += 1
            docs_info_list.append([current_page * results_per_page, results_per_page])

            if current_page == max_page_hit:
                break

        # Makes a JSON from the list of URLs and send it to the queue as a job
        r.add_to_queue(json.dumps([''.join(random.choices(string.ascii_letters + string.digits, k=16)),
                                   'docs',
                                   docs_info_list]))


def expired_job_checker():  # user EXPIRE

    logger.info('Checking for expired jobs...')
    logger.debug('Awake: %s', 'expire: expire is active', extra=d)
    logger.debug('Calling Function: %s', 'expire: attempting to find expired', extra=d)
    r.find_expired()
    logger.debug('Function Successful: %s', 'expire: find expired successfully', extra=d)
    logger.debug('Sleep: %s', 'expire: sleep for 1 hours', extra=d)
    logger.info('Returning to sleep')


def run():

    get_work(1000)

    while True:
        expired_job_checker()
        time.sleep(3600)
