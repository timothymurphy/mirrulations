import os
from threading import Thread


def main():

    def run_redis():
        os.system('redis-server')

    def run_flask():
        from mirrulations_server.flask_manager import run
        run()

    def run_work():
        from mirrulations_server.work_manager import monolith
        from mirrulations_server.expire import expire
        monolith()
        expire()

    Thread(target=run_redis).start()
    Thread(target=run_flask).start()
    Thread(target=run_work).start()


if __name__ == '__main__':
    main()
