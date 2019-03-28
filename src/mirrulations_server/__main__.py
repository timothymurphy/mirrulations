import os
from threading import Thread

from mirrulations_server.flask_manager import FLASK_APP


def main():

    def run_redis():
        os.system('redis-server')

    def run_flask():
        FLASK_APP.run('0.0.0.0', '8080')

    def run_work():
        from mirrulations_server.work_manager import run
        run()

    Thread(target=run_redis).start()
    Thread(target=run_flask).start()
    Thread(target=run_work).start()


if __name__ == '__main__':
    main()
