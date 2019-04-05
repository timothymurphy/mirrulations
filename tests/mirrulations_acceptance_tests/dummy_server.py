from flask import Flask, request
import random
import string
import json
from mirrulations_core.mirrulations_logging import logger

app = Flask(__name__)
version = 'v1.3'


@app.route('/')
def default():
    pass


@app.route('/get_work')
def get_work():
    logger.warning('Successful API Call: %s', 'get_work: get_work')
    if len(request.args) != 1:
        logger.error('Incorrect number of parameters')
        return 'Parameter Missing', 400
    client_id = request.args.get('client_id')
    if client_id is None:
        logger.warning('Exception: %s',
                       'get_work: BadParameterException, '
                       'client id was none')
        logger.error('Error - no client ID')
        return 'Bad Parameter', 400
    job_id = ''.join(random.choice(string.ascii_uppercase + string.digits)
                         for _ in range(16))
    type = "docs"
    data = ["https://api.data.gov/regulations/v3/documents.json?rpp=5&po=0"]
    converted_json = {
        'job_id': job_id,
        'type': type,
        'data': data,
        'version': version
    }
    json_info = json.dumps(converted_json)
    return json_info


@app.route('/return_docs', methods=['POST'])
def return_docs():
    pass


@app.route('/return_doc', methods=['POST'])
def return_doc():
    pass


def run():
    app.run('0.0.0.0', '8080')


if __name__ == '__main__':
    run()
