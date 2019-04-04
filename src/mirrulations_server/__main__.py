import os
from threading import Thread

from mirrulations_core.config import server_config_setup

from mirrulations_server.docs_work_gen import monolith
from mirrulations_server.endpoints import run
from mirrulations_server.expire import expire


def main(do_config_setup):

    if do_config_setup:
        server_config_setup()

    def run_redis():
        os.system('redis-server')

    def run_flask():
        run()

    def run_work():
        monolith()
        expire()

    Thread(target=run_redis).start()
    Thread(target=run_flask).start()
    Thread(target=run_work).start()
