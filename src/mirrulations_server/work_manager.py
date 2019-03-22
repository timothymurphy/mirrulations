import json
import logging
import random
import redis
import string
import time
from mirrulations_server.redis_manager import RedisManager
from mirrulations_core.api_call_manager import APICallManager
import mirrulations_core.config as config

key = config.read_value('SERVER', 'API_KEY')

redis_manager = RedisManager(redis.Redis())
api_manager = APICallManager(key)


def get_max_page_hit(results_per_page):

    try:
        records = api_manager.make_documents_call(counts_only=True, results_per_page=results_per_page).json
        return records["totalNumRecords"] // results_per_page
    except api_manager.CallFailException:
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
        redis_manager.add_to_queue(json.dumps([''.join(random.choices(string.ascii_letters + string.digits, k=16)),
                                   'docs',
                                               docs_info_list]))


def run():

    get_work(1000)

    while True:
        redis_manager.find_expired()
        time.sleep(3600)
