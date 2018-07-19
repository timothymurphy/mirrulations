from flask import Flask, request, Response
import redis
import json
from docs_filter import process_docs
from doc_filter import process_doc
from redis_manager import RedisManager


app = Flask(__name__)


r = RedisManager(redis.Redis())


@app.route('/')
def default():
    """
    Default endpoint
    :return: returns empty json
    """
    return json.dumps({})


@app.route('/get_work')
def get_work():
    """
    endpoint the user will use to get work from the queue
    client_id will be one of the parameters given for logging purposes
    :return: returns the json containing the job_id, the type of work to be done, the work that nees to be done, and
    the version number
    """
    if len(request.args) != 1:
        raise GetException
    client_id = request.args.get('client_id')
    if client_id is None:
        raise BadParameterException
    work_list = r.get_work()
    json_info = generate_json(work_list)
    return json_info


@app.route('/return_docs', methods=['POST'])
def return_docs():
    """
    the endpoint the client calls to return the document ids received from the regulations docs calls
    :return: returns a string saying successful so the client knows the call was successful
    """
    try:
        json_info = request.get_json()
    except:
        raise BadParameterException
    if json_info is None:
        raise PostException
    process_docs(json_info, r)
    return 'Successful!'


@app.route('/return_doc', methods=['POST'])
def return_doc():
    """
    the endpoint the client calls to return documents they received from the individual regulations doc calls
    :return: returns a string saying successful so the client knows the call was successful
    """
    try:
        files = request.files['file']
        json_info= request.form['json_info']
    except:
        raise BadParameterException
    process_doc(json_info, files, r)
    return 'Successful!'


def generate_json(work_list):
    """
    given a list of values, the list will be converted into json format
    :param list: the list of values that will be converted into json
    :return: returns the json formatted list
    """
    job_id = work_list[0]
    type = work_list[1]
    data = work_list[2]
    converted_json = {
        "job_id": job_id,
        "type": type,
        "data": data,
        "version": "v0.1"
    }
    return json.dumps(converted_json)


# Throw exception if there is an error making the get call
class GetException(Exception):
    print("Bad Request")

# Throw exception if one of the parameters is incorrect
class BadParameterException(Exception):
    print("Bad Request")

# Throw exception if there was an error making the post request
class PostException(Exception):
    print("Bad Request")


if __name__ == '__main__':
    app.run('10.76.100.45', port=6060)



