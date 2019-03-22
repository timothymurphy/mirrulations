import io
from flask import Flask, request
import redis
import json
from mirrulations_server.docs_filter import process_docs
from mirrulations_server.doc_filter import process_doc
from mirrulations_server.redis_manager import RedisManager
from mirrulations.mirrulations_logging import logger


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
    logger.warning("Successful API Call: %s", 'get_work: get_work')
    if len(request.args) != 1:
        logger.error('Error - number of parameters incorrect')
        return 'Parameter Missing', 400
    client_id = request.args.get('client_id')
    if client_id is None:
        logger.warning("Exception: %s", 'get_work: BadParameterException, client id was none')
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


def run():
    app.run('0.0.0.0', '8080')
