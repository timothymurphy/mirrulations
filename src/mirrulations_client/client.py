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
from mirrulations_core.mirrulations_logging import logger

API_KEY = config.read_value('CLIENT', 'API_KEY')
CLIENT_ID = config.read_value('CLIENT', 'CLIENT_ID')
SERVER_ADDRESS = config.read_value('CLIENT', 'SERVER_ADDRESS')
VERSION = "v1.3"


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
            logger.info('No work, sleeping...')
            time.sleep(3600)
        else:
            logger.info('Work is ' + work_type + ' job')

            if work_type == 'doc':
                return_doc(work_json)
            else:
                return_docs(work_json)

        client_health_manager.make_call()

    else:
        logger.error('Job type unexpected')
        client_health_manager.make_fail_call()


def get_json_info(json_result):
    """
    Return job information from server json
    :param json_result: the json returned from
    """

    job_id = json_result["job_id"]
    data = json_result["data"]
    return job_id, data


def return_docs(json_result):
    """
    Handles the documents processing necessary for a job
    Calls the /return_docs endpoint of the server to return data for the job it completed
    :param json_result: the json received from the /get_work endpoint
    :return: result from calling /return_docs
    """

    job_id, data = get_json_info(json_result)
    json_info = docs.documents_processor(api_manager, data, job_id, client_id)
    path = tempfile.TemporaryDirectory()
    add_client_log_files(path.name, ".")
    shutil.make_archive("result", "zip", path.name)
    file_obj = open('result.zip', 'rb')
    r = server_manager.make_docs_return_call(file_obj, json_info)
    r.raise_for_status()
    return r


def return_doc(json_result):
    """
    Handles the document processing necessary for a job
    Calls the /return_doc endpoint of the server to return data for the job it completed
    :param json_result: the json received from the /get_work endpoint
    :return: result from calling /return_doc
    """

    job_id, doc_dicts = get_json_info(json_result)
    doc_ids = []
    for dic in doc_dicts:
        doc_ids.append(dic['id'])
    path = doc.document_processor(api_manager, doc_ids)
    add_client_log_files(path.name, ".")
    shutil.make_archive("result", "zip", path.name)
    file_obj = open('result.zip', 'rb')
    json_info = {'job_id': job_id, 'type': 'doc', 'user': CLIENT_ID, 'version': VERSION}
    r = server_manager.make_doc_return_call(file_obj, json_info)
    r.raise_for_status()
    return r


def copy_file_safely(directory, file_path):
    """
    Safely copies a file to a directory; if the file isn't there to be copied, it won't be copied.
    :param directory: Directory to copy to
    :param file_path: File to copy
    """

    if Path(filepath).exists():
        if Path(directory).exists():
            shutil.copy(filepath, directory)
        else:
            logger.warning('File not copied, directory does not exist')
    else:
        logger.warning('File not copied, file does not exist')


def add_client_log_files(directory, log_directory):
    """
    Used to copy client log files into the temp directory to be sent to the server.
    :param directory: Directory to write files to
    :param log_directory: Directory to get files from
    """

    copy_file_safely(directory, log_directory + "/client.log")
    copy_file_safely(directory, log_directory + "/document_processor.log")
    copy_file_safely(directory, log_directory + "/documents_processor.log")
    copy_file_safely(directory, log_directory + "/api_call.log")
    copy_file_safely(directory, log_directory + "/api_call_management.log")



def run():
    """
    Working loop
    Get work - Determine type of work - Do work - Return work
    If there is no work in the server, sleep for an hour
    """


    while True:

        try:
            work = get_work()
        except api_manager.CallFailException:
            logger.debug("API Call Failed...")
            logger.info("Waiting an hour until retry...")
            time.sleep(3600)
            continue

        client_health_manager.make_call()
        work_json = json.loads(work.content.decode('utf-8'))

        do_work(work_json)
