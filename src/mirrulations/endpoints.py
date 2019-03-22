from flask import Flask, request
import redis
import json
from mirrulations.docs_filter import process_docs
from mirrulations.doc_filter import process_doc
from mirrulations.redis_manager import RedisManager
import logging
import io


FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='endpoints_log.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': 'FLASK'}
logger = logging.getLogger('tcpserver')

app = Flask(__name__)

version = 'v1.3'


def redis_server():
    return RedisManager(redis.Redis())


@app.route('/')
def default():
    """
    Default endpoint
    :return: Returns empty json
    """
    return json.dumps({})


@app.route('/get_work')
def get_work():
    """
    Endpoint the user will use to get work from the queue
    client_id will be one of the parameters given for logging purposes
    :return: Returns the json containing the job_id, the type of work to be done, the work that nees to be done, and
    the version number
    """
    logging.warning("Successful API Call: %s", 'get_work: get_work', extra=d)
    if len(request.args) != 1:
        logger.error('Error - number of parameters incorrect')
        return 'Parameter Missing', 400
    client_id = request.args.get('client_id')
    if client_id is None:
        logging.warning("Exception: %s", 'get_work: BadParameterException, client id was none', extra=d)
        logger.error('Error - no client ID')
        return 'Bad Parameter', 400
    json_info = redis_server().get_work()
    return json.dumps(json_info)


@app.route('/return_docs', methods=['POST'])
def return_docs():
    """
    The endpoint the client calls to return the document ids received from the regulations docs calls
    :return: Returns a string saying successful so the client knows the call was successful
    """
    try:
        json_info = request.form['json']
        files = request.files['file'].read()
    except:
        logger.error('Error - bad parameter')
        return 'Bad Parameter', 400
    if json_info is None:
        logger.error('Error - could not post docs')
        return 'Bad Parameter', 400
    files = io.BytesIO(files)
    process_docs(redis_server(), json.loads(json_info), files)
    return 'Successful!'


@app.route('/return_doc', methods=['POST'])
def return_doc():
    """
    The endpoint the client calls to return documents they received from the individual regulations doc calls
    :return: Returns a string saying successful so the client knows the call was successful
    """

    try:
        files = request.files['file'].read()
        json_info= request.form['json']
    except:
        logger.error('Error - bad parameter')
        return 'Bad Parameter', 400
    files = io.BytesIO(files)
    process_doc(redis_server(), json.loads(json_info), files)
    return 'Successful!'


def generate_json(work_list):
    """
    Given a list of values, the list will be converted into json format
    :param work_list: The list of values that will be converted into json
    :return: Returns the json formatted list
    """
    job_id = work_list[0]
    type = work_list[1]
    data = work_list[2]
    converted_json = {
        "job_id": job_id,
        "type": type,
        "data": data,
        "version": version
    }
    return json.dumps(converted_json)


def run():
    app.run('0.0.0.0', '8080')


if __name__ == '__main__':
    run()
