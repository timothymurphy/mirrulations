import mirrulations_client.document_processor as doc
import mirrulations_client.documents_processor as docs
from mirrulations_client.server_call_manager import ServerCallManager
from mirrulations_core.api_call_manager import APICallManager
import requests
import json
import time
import logging
import shutil
import tempfile
from pathlib import Path
import mirrulations_core.config as config

API_KEY = config.read_value('CLIENT', 'API_KEY')
CLIENT_ID = config.read_value('CLIENT', 'CLIENT_ID')
SERVER_ADDRESS = config.read_value('CLIENT', 'SERVER_ADDRESS')
VERSION = "v1.3"

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='client.log', format=FORMAT)
d = {'clientip': '192.168.0.1', 'user': CLIENT_ID}
logger = logging.getLogger('tcpserver')


class ClientHealthCallManager:

    def __init__(self):
        self.base_url = 'https://hc-ping.com/457a1034-83d4-4a62-8b69-c71060db3a08'

    def make_call(self):
        requests.get(self.base_url)

    def make_fail_call(self):
        requests.get(self.base_url + '/fail')


api_manager = APICallManager(API_KEY)
server_manager = ServerCallManager(CLIENT_ID, SERVER_ADDRESS)
client_health_manager = ClientHealthCallManager()


def get_work():
    """
    Calls the /get_work endpoint of the server to fetch work to process
    :return: the result of making a call to get work
    """
    logger.debug('Returning: %s', 'get_work: the respond from the api call to get_work', extra=d)
    work = server_manager.make_work_call()
    logger.debug('Call Successful: %s', 'get_work: call made successfully', extra=d)

    return work


def do_work(work_json):

    work_type = work_json['type']

    if work_type in ['doc', 'docs', 'none']:

        if work_type == 'none':
            logger.debug('Function Successful: %s', 'do_work: sleep due to no work', extra=d)
            logger.info('No work, sleeping...')
            time.sleep(3600)
        else:
            logger.debug('Calling Function: %s', 'do_work: call return_' + work_type, extra=d)
            logger.info('Work is ' + work_type + ' job')

            if work_type == 'doc':
                return_doc(work_json)
            else:
                return_docs(work_json)

            logger.debug('Function Successful: %s', 'do_work: return_' + work_type + ' call successful', extra=d)

        client_health_manager.make_call()

    else:

        logger.debug('Exception: %s', 'do_work: type specified in json object was not in - doc, docs, none')
        logger.error('Job type unexpected')

        client_health_manager.make_fail_call()


def get_json_info(json_result):
    """
    Return job information from server json
    :param json_result: the json returned from
    """
    logger.debug('Call Successful: %s', 'get_json_info: call made successfully', extra=d)
    logger.debug('Assign Variable: %s', 'get_json_info: get the job id from ', extra=d)

    logger.info('Collecting job information...')

    job_id = json_result["job_id"]

    logger.debug('Variable Success: %s', 'get_json_info: job_id retrieved from result json', extra=d)
    logger.debug('Assign Variable: %s', 'get_json_info: get the data from get work endpoint', extra=d)

    data = json_result["data"]

    logger.debug('Variable Success: %s', 'get_json_info: data retrieved from result json', extra=d)
    logger.debug('Returning: %s', 'get_json_info: returning job id and data from get work', extra=d)

    logger.info('Job information retrieved')

    return job_id, data


def return_docs(json_result):
    """
    Handles the documents processing necessary for a job
    Calls the /return_docs endpoint of the server to return data for the job it completed
    :param json_result: the json received from the /get_work endpoint
    :return: result from calling /return_docs
    """
    logger.info('Returning documents data to server...')

    logger.debug('Call Successful: %s', 'return_docs: call made successfully', extra=d)
    logger.debug('Calling Function: %s','return_docs: call get_json_info for job id and urls',extra=d)

    job_id, docs_info_list = get_json_info(json_result)

    logger.debug('Function Successful: %s', 'return_docs: job_id and urls retrieved successfully', extra=d)
    logger.debug('Calling Function: %s','return_docs: call documents_processor',extra=d)

    json_info = docs.documents_processor(api_manager, docs_info_list, job_id, CLIENT_ID)

    logger.debug('Function Successful: %s', 'return_docs: successful call to documents processor', extra=d)

    logger.debug('Assign Variable: %s', 'return_docs: making the tempfile', extra=d)
    path = tempfile.TemporaryDirectory()
    logger.debug('Variable Success: %s', 'return_docs: tempfile successfully made', extra=d)
    logger.debug('Calling function: %s', 'return_docs: call add_client_log', extra=d)
    add_client_log_files(path.name, ".")
    logger.debug('Function Successful: %s', 'return_docs: add_client_log completed', extra=d)
    logger.debug('Attempt Archive: %s', 'return_docs: attempting to make the archive', extra=d)
    shutil.make_archive("result", "zip", path.name)
    logger.debug('Archive Success: %s', 'return_docs: archive successfully made', extra=d)
    logger.debug('Assign Variable: %s', 'return_docs: opening the zip file to send', extra=d)
    file_obj = open('result.zip', 'rb')
    logger.debug('Variable Success: %s', 'return_docs: zip file opened', extra=d)

    logger.debug('Calling Function: %s', 'return_docs: post to /return_docs endpoint', extra=d)
    r = server_manager.make_docs_return_call(file_obj, json_info)
    logger.debug('Function Successful: %s', 'return_docs: successful call to /return_doc', extra=d)

    r.raise_for_status()

    logger.debug('Returning: %s', 'return_docs: returning information from the call to /return_docs', extra=d)
    logger.info('Documents data returned')

    return r


def return_doc(json_result):
    """
    Handles the document processing necessary for a job
    Calls the /return_doc endpoint of the server to return data for the job it completed
    :param json_result: the json received from the /get_work endpoint
    :return: result from calling /return_doc
    """
    logger.info('Returning document data to server...')

    logger.debug('Call Successful: %s', 'return_doc: call made successfully', extra=d)
    logger.debug('Calling Function: %s','return_doc: call get_json_info for job id and urls',extra=d)

    job_id, doc_dicts = get_json_info(json_result)

    logger.debug('Function Successful: %s', 'return_doc: job_id and document ids retrieved successfully', extra=d)
    logger.debug('Assign Variable: %s', 'return_doc: attempting to get document ids from each json', extra=d)

    doc_ids = []
    for dic in doc_dicts:

        logger.debug('Assign Variable: %s', 'return_doc: attempting to get each document id from each json', extra=d)

        doc_ids.append(dic['id'])

        logger.debug('Variable Success: %s', 'return_doc: document id added to the list', extra=d)

    logger.debug('Variable Success: %s', 'return_doc: list of document ids was created', extra=d)

    logger.debug('Function Successful: %s', 'return_doc: result.zip created successfully', extra=d)
    logger.debug('Calling Function: %s', 'return_doc: call document_processor with the list of document ids', extra=d)

    path = doc.document_processor(api_manager, doc_ids)

    add_client_log_files(path.name, ".")
    logger.debug('Function Successful: %s', 'return_doc: document_processor executed successfully', extra=d)

    logger.debug('File Create Attempt: %s', 'return_doc: attempting to create the zip file', extra=d)
    logger.info('Attempting to create doc file...')

    shutil.make_archive("result", "zip", path.name)
    logger.debug('File Creation Successful: %s', "return_doc: successfully created the zip file", extra=d)
    logger.debug('Assign Variable: %s', 'return_doc: opening the zip', extra=d)
    file_obj = open('result.zip', 'rb')
    logger.debug('Variable Success: %s', 'return_doc: zip opened', extra=d)
    logger.debug('Calling Function: %s', 'return_doc: post to /return_doc endpoint', extra=d)
    json_info = {'job_id': job_id, 'type': 'doc', 'user': CLIENT_ID, 'version': VERSION}
    r = server_manager.make_doc_return_call(file_obj, json_info)

    logger.info('Doc file created')

    logger.debug('Function Successful: %s', 'return_doc: successful call to /return_doc', extra=d)
    logger.debug('Calling Function: %s','return_doc: Raise Exception for bad status code',extra=d)

    r.raise_for_status()

    logger.debug('Returning: %s', 'return_doc: returning information from the call to /return_docs', extra=d)

    logger.info('Document data returned')

    return r


def copy_file_safely(directory, file_path):
    """
    Safely copies a file to a directory; if the file isn't there to be copied, it won't be copied.
    :param directory: Directory to copy to
    :param file_path: File to copy
    """

    logger.info('Copying file...')
    if Path(file_path).exists():
        if Path(directory).exists():
            shutil.copy(file_path, directory)
            logger.debug('Call Successful: %s', 'copy_file_safely: File copied.', extra=d)
            logger.info('File copied')
        else:
            logger.debug('Exception: %s', 'copy_file_safely: Directory does not exist. Not copying.', extra=d)
            logger.warning('File not copied, directory does not exist')
    else:
        logger.debug('Exception: %s', 'copy_file_safely: No file exists. Not copying.', extra=d)
        logger.warning('File not copied, file does not exist')


def add_client_log_files(directory, log_directory):
    """
    Used to copy client log files into the temp directory to be sent to the server.
    :param directory: Directory to write files to
    :param log_directory: Directory to get files from
    """
    logger.info('Copying log files...')

    logger.debug('Calling Function: %s', 'copy_file_safely: copying client.log to tempfile', extra=d)
    copy_file_safely(directory, log_directory + "/client.log")
    logger.debug('Calling Function: %s', 'copy_file_safely: copying document_processor.log to tempfile', extra=d)
    copy_file_safely(directory, log_directory + "/document_processor.log")
    logger.debug('Calling Function: %s', 'copy_file_safely: copying documents_processor.log to tempfile', extra=d)
    copy_file_safely(directory, log_directory + "/documents_processor.log")
    logger.debug('Calling Function: %s', 'copy_file_safely: copying api_call.log to tempfile', extra=d)
    copy_file_safely(directory, log_directory + "/api_call.log")
    logger.debug('Calling Function: %s', 'copy_file_safely: copying api_call_management.log to tempfile', extra=d)
    copy_file_safely(directory, log_directory + "/api_call_management.log")

    logger.info('Log files copied')


def run():
    """
    Working loop
    Get work - Determine type of work - Do work - Return work
    If there is no work in the server, sleep for an hour
    """
    logger.debug('Call Successful: %s', 'run: called successfully', extra=d)
    logger.info('Beginning client process...')

    while True:

        try:
            logger.debug('Calling Function: %s', 'run: call to get_work', extra=d)
            logger.info('Attempting to retrieve work...')
            work = get_work()
            logger.debug('Function Successful: %s', 'run: api call successful', extra=d)
            logger.info('Work successfully retrieved')
        except api_manager.CallFailException:
            logger.debug("API Call Failed...")
            logger.info("Waiting an hour until retry...")
            time.sleep(3600)
            continue

        client_health_manager.make_call()

        logger.debug('Assign Variable: %s', 'run: decode the json variable from get_work', extra=d)
        work_json = json.loads(work.content.decode('utf-8'))
        logger.debug('Variable Success: %s', 'run: decode the json of work successfully', extra=d)

        do_work(work_json)
        logger.debug('Function Successful: %s', 'run: successful iteration in do work', extra=d)
        logger.info('Work completed')
