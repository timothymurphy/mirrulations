from flask import request
import io
import json

from mirrulations_server.doc_filter import process_doc
from mirrulations_server.docs_filter import process_docs

from mirrulations_core import LOGGER
from mirrulations_server import FLASK_APP, REDIS_MANAGER


@FLASK_APP.route('/')
def default():
    """
    Default endpoint
    :return: Returns empty json
    """
    return json.dumps({})


@FLASK_APP.route('/get_work')
def get_work():
    """
    Endpoint the user will use to get work from the queue
    client_id will be one of the parameters given for logging purposes
    :return: Returns the json containing the job_id, the type of work to be done, the work that needs to be done, and
    the version number
    """
    LOGGER.warning("Successful API Call: %s", 'get_work: get_work')
    if len(request.args) != 1:
        LOGGER.error('Error - number of parameters incorrect')
        return 'Parameter Missing', 400
    client_id = request.args.get('client_id')
    if client_id is None:
        LOGGER.warning("Exception: %s", 'get_work: BadParameterException, client id was none')
        LOGGER.error('Error - no client ID')
        return 'Bad Parameter', 400
    json_info = REDIS_MANAGER.get_work()
    return json.dumps(json_info)


@FLASK_APP.route('/return_docs', methods=['POST'])
def return_docs():
    """
    The endpoint the client calls to return the document ids received from the regulations docs calls
    :return: Returns a string saying successful so the client knows the call was successful
    """
    try:
        json_info = request.form['json']
        files = request.files['file'].read()
    except:
        LOGGER.error('Error - bad parameter')
        return 'Bad Parameter', 400
    if json_info is None:
        LOGGER.error('Error - could not post docs')
        return 'Bad Parameter', 400
    files = io.BytesIO(files)
    process_docs(REDIS_MANAGER, json.loads(json_info), files)
    return 'Successful!'


@FLASK_APP.route('/return_doc', methods=['POST'])
def return_doc():
    """
    The endpoint the client calls to return documents they received from the individual regulations doc calls
    :return: Returns a string saying successful so the client knows the call was successful
    """

    try:
        files = request.files['file'].read()
        json_info = request.form['json']
    except:
        LOGGER.error('Error - bad parameter')
        return 'Bad Parameter', 400
    files = io.BytesIO(files)
    process_doc(REDIS_MANAGER, json.loads(json_info), files)
    return 'Successful!'
