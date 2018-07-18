from api_call_managment import *
import json

workfiles = []
version = "v1.0"


def documents_processor(urls, job_id, client_id):
    """
    Call each url in the list, process the results of the calls and then form a json file to send back the results
    :param urls: list of urls that have to be called
    :param job_id: the id of the job that is being worked on currently
    :param client_id: id of the client calling this function
    :return result: the json to be returned to the server after each call is processed
    """
    global workfiles
    workfiles = []
    for url in urls:
        result = api_call_manager(add_api_key(url))
        process_results(result)
    result = json.loads(json.dumps({"job_id" : job_id, "data" : workfiles, "client_id" : str(client_id), "version" : version}))
    return result


def process_results(result):
    """
    Loads the json from the results of the api call
    Gets the list of documents from the json
    Creates a new json that contains the documents returned from each api call
    :param result: Result of the api call
    :return: returns True if the processing completed successfully
    """
    docs_json = load_json(result)
    try:
        doc_list = docs_json["documents"]
    except TypeError:
        raise BadJsonException

    for doc in doc_list:
        doc = {"id" : doc["documentId"], "count" : doc["attachmentCount"] + 1}
        workfiles.append(doc)

    return True


def load_json(result):
    """
    loads the json format from the result of the api call
    :param result: the result of the api call
    :return: returns the json format of the api call
    """
    try:
        docs_json = json.loads(result.text)
    except json.JSONDecodeError:
        raise BadJsonException
    return docs_json


# Raised if the json is not correctly formatted or is empty
class BadJsonException(Exception):
    print("NOTICE: The Json appears to be formatted incorrectly.")
