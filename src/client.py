import document_processor as doc
import documents_processor as docs
import api_call_management as man
import requests
import json
import os
import time
import logging
import shutil
import config
import tempfile
from pathlib import Path

# These variables are specific to the current implementation
version = "v1.3"
serverurl = "http://" + config.read_value("ip") + ":" + config.read_value("port")
home = os.getenv("HOME")
with open(home + '/.env/regulationskey.txt') as f:
    key = f.readline().strip()
    client_id = f.readline().strip()

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='client.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': client_id}
logger = logging.getLogger('tcpserver')

client_health_url = "https://hc-ping.com/457a1034-83d4-4a62-8b69-c71060db3a08"


def get_work(client_id):
    """
    Calls the /get_work endpoint of the server to fetch work to process
    :param client_id: the id of the client calling /get_work
    :return: the result of making a call to get work
    """
    global d

    logger.warning('Call Successful: %s', 'get_work: call made successfully', extra=d)
    logger.warning('Assign Variable: %s', 'get_work: create the url for getting work', extra=d)

    url = serverurl+"/get_work?client_id="+str(client_id)

    logger.warning('Variable Success: %s', 'get_work: url created successfully for get work', extra=d)
    logger.warning('Returning: %s', 'get_work: the respond from the api call to get_work', extra=d)
    return man.api_call_manager(url)


def get_json_info(json_result):
    """
    Return job information from server json
    :param json_result: the json returned from
    :return:
    """
    global d

    logger.warning('Call Successful: %s', 'get_json_info: call made successfully', extra=d)
    logger.warning('Assign Variable: %s', 'get_json_info: get the job id from ', extra=d)

    job_id = json_result["job_id"]

    logger.warning('Variable Success: %s', 'get_json_info: job_id retrieved from result json', extra=d)
    logger.warning('Assign Variable: %s', 'get_json_info: get the data from get work endpoint', extra=d)

    urls = json_result["data"]

    logger.warning('Variable Success: %s', 'get_json_info: data retrieved from result json', extra=d)
    logger.warning('Returning: %s', 'get_json_info: returning job id and data from get work', extra=d)

    return job_id, urls


def return_docs(json_result, client_id):
    """
    Handles the documents processing necessary for a job
    Calls the /return_docs endpoint of the server to return data for the job it completed
    :param json_result: the json received from the /get_work endpoint
    :param client_id: the id of the client that is processing the documents job
    :return: result from calling /return_docs
    """
    global d
    logger.warning('Call Successful: %s', 'return_docs: call made successfully', extra=d)

    logger.warning('Calling Function: %s','return_docs: call get_json_info for job id and urls',extra=d)

    job_id, urls = get_json_info(json_result)

    logger.warning('Function Successful: %s', 'return_docs: job_id and urls retrieved successfully', extra=d)
    logger.warning('Calling Function: %s','return_docs: call documents_processor',extra=d)

    json_info = docs.documents_processor(urls,job_id,client_id)

    logger.warning('Function Successful: %s', 'return_docs: successful call to documents processor', extra=d)

    logger.warning('Assign Variable: %s', 'return_docs: making the tempfile', extra=d)
    path = tempfile.TemporaryDirectory()
    logger.warning('Variable Success: %s', 'return_docs: tempfile successfully made', extra=d)
    logger.warning('Calling function: %s', 'return_docs: call add_client_log', extra=d)
    add_client_log_files(path.name, ".")
    logger.warning('Function Successful: %s', 'return_docs: add_client_log completed', extra=d)
    logger.warning('Attempt Archive: %s', 'return_docs: attempting to make the archive', extra=d)
    shutil.make_archive("result", "zip", path.name)
    logger.warning('Archive Success: %s', 'return_docs: archive successfully made', extra=d)
    logger.warning('Assign Variable: %s', 'return_docs: opening the zip file to send', extra=d)
    fileobj = open('result.zip', 'rb')
    logger.warning('Variable Success: %s', 'return_docs: zip file opened', extra=d)

    logger.warning('Calling Function: %s', 'return_docs: post to /return_docs endpoint', extra=d)
    r = requests.post(serverurl + "/return_docs", files={'file': fileobj}, data={'json':json.dumps(json_info)})
    logger.warning('Function Successful: %s', 'return_docs: successful call to /return_doc', extra=d)

    r.raise_for_status()

    logger.warning('Returning: %s', 'return_docs: returning information from the call to /return_docs', extra=d)

    return r


def return_doc(json_result, client_id):
    """
    Handles the document processing necessary for a job
    Calls the /return_doc endpoint of the server to return data for the job it completed
    :param json_result: the json received from the /get_work endpoint
    :param client_id: the id of the client that is processing the documents job
    :return: result from calling /return_doc
    """
    global d

    logger.warning('Call Successful: %s', 'return_doc: call made successfully', extra=d)
    logger.warning('Calling Function: %s','return_doc: call get_json_info for job id and urls',extra=d)

    job_id, doc_dicts = get_json_info(json_result)

    logger.warning('Function Successful: %s', 'return_doc: job_id and document ids retrieved successfully', extra=d)
    logger.warning('Assign Variable: %s', 'return_doc: attempting to get document ids from each json', extra=d)

    doc_ids = []
    for dic in doc_dicts:

        logger.warning('Assign Variable: %s', 'return_doc: attempting to get each document id from each json', extra=d)

        doc_ids.append(dic['id'])

        logger.warning('Variable Success: %s', 'return_doc: document id added to the list', extra=d)

    logger.warning('Variable Success: %s', 'return_doc: list of document ids was created', extra=d)

    logger.warning('Function Successful: %s', 'return_doc: result.zip created successfully', extra=d)
    logger.warning('Calling Function: %s', 'return_doc: call document_processor with the list of document ids', extra=d)

    path = doc.document_processor(doc_ids)

    add_client_log_files(path.name, ".")
    logger.warning('Function Successful: %s', 'return_doc: document_processor executed successfully', extra=d)

    logger.warning('File Create Attempt: %s', 'return_doc: attempting to create the zip file', extra=d)
    shutil.make_archive("result", "zip", path.name)
    logger.warning('File Creation Successful: %s', "return_doc: successfully created the zip file", extra=d)
    logger.warning('Assign Variable: %s', 'return_doc: opening the zip', extra=d)
    fileobj = open('result.zip', 'rb')
    logger.warning('Variable Success: %s', 'return_doc: zip opened', extra=d)
    logger.warning('Calling Function: %s', 'return_doc: post to /return_doc endpoint', extra=d)
    r = requests.post(serverurl+"/return_doc",
                      files={'file':('result.zip', fileobj)},
                      data={'json':json.dumps({"job_id" : job_id, "type" : "doc",
                                               "client_id": client_id, "version" : version })})

    logger.warning('Function Successful: %s', 'return_doc: successful call to /return_doc', extra=d)
    logger.warning('Calling Function: %s','return_doc: Raise Exception for bad status code',extra=d)

    r.raise_for_status()

    logger.warning('Returning: %s', 'return_doc: returning information from the call to /return_docs', extra=d)

    return r


def copy_file_safely(directory, filepath):
    """
    Safely copies a file to a directory; if the file isn't there to be copied, it won't be copied.
    :param directory: Directory to copy to
    :param filepath: File to copy
    """

    if Path(filepath).exists():
        if Path(directory).exists():
            shutil.copy(filepath, directory)
            logger.warning('Call Successfuly: %s', 'copy_file_safely: File copied.', extra=d)
        else:
            logger.warning('Exception: %s', 'copy_file_safely: Directory does not exist. Not copying.', extra=d)
    else:
        logger.warning('Exception: %s', 'copy_file_safely: No file exists. Not copying.', extra=d)


def add_client_log_files(directory, log_directory):
    """
    Used to copy client log files into the temp directory to be sent to the server.
    :param directory: Directory to write files to
    :param log_directory: Directory to get files from
    :return:
    """
    logger.warning('Calling Function: %s', 'copy_file_safely: copying client.log to tempfile', extra=d)
    copy_file_safely(directory, log_directory + "/client.log")
    logger.warning('Calling Function: %s', 'copy_file_safely: copying document_processor.log to tempfile', extra=d)
    copy_file_safely(directory, log_directory + "/document_processor.log")
    logger.warning('Calling Function: %s', 'copy_file_safely: copying documents_processor.log to tempfile', extra=d)
    copy_file_safely(directory, log_directory + "/documents_processor.log")
    logger.warning('Calling Function: %s', 'copy_file_safely: copying api_call.log to tempfile', extra=d)
    copy_file_safely(directory, log_directory + "/api_call.log")
    logger.warning('Calling Function: %s', 'copy_file_safely: copying api_call_management.log to tempfile', extra=d)
    copy_file_safely(directory, log_directory + "/api_call_management.log")


def do_work():
    """
    Working loop
    Get work - Determine type of work - Do work - Return work
    If there is no work in the server, sleep for an hour
    :return:
    """
    logger.warning('Call Successful: %s', 'do_work: called successfully', extra=d)

    while True:

        logger.warning('Calling Function: %s', 'do_work: call to get_work function', extra=d)
        try:
            work = get_work(client_id)

            logger.warning('Function Successful: %s', 'do_work: get_work call successful', extra=d)
            requests.get(client_health_url)
            logger.warning('Assign Variable: %s', 'do_work: decode the json variable from get_work', extra=d)

            work_json = json.loads(work.content.decode('utf-8'))

            logger.warning('Variable Success: %s', 'do_work: decode the json of work successfully', extra=d)
        except man.CallFailException:
            time.sleep(3600)

        if work_json["type"] == "doc":

            logger.warning('Calling Function: %s', 'do_work: call return_doc', extra=d)

            r = return_doc(work_json, client_id)

            logger.warning('Function Successful: %s', 'do_work: return_doc call successful', extra=d)

            requests.get(client_health_url)

        elif work_json["type"] == "docs":

            logger.warning('Calling Function: %s', 'do_work: call return_docs', extra=d)

            r = return_docs(work_json, client_id)

            logger.warning('Function Successful: %s', 'do_work: return_docs call successful', extra=d)

            requests.get(client_health_url)

        elif work_json["type"] == "none":

            logger.warning('Function Successful: %s', 'do_work: sleep due to no work', extra=d)

            time.sleep(3600)

            requests.get(client_health_url)

        else:

            logger.warning('Exception: %s', 'do_work: type specified in json object was not in - doc, docs, none')
            requests.get(client_health_url + "/fail")
        logger.warning('Function Successful: %s', 'do_work: successful iteration in do work', extra=d)


if __name__ == '__main__':
    do_work()
