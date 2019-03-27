import json
from pathlib import Path
import shutil
import tempfile
import time

import mirrulations_client.document_processor as doc
import mirrulations_client.documents_processor as docs

from mirrulations_core import VERSION, LOGGER
from mirrulations_client import CLIENT_ID, API_MANAGER, CLIENT_HEALTH_MANAGER, SERVER_MANAGER


def do_work(work_json):

    work_type = work_json['type']

    if work_type in ['doc', 'docs', 'none']:

        if work_type == 'none':
            LOGGER.info('No work, sleeping...')
            time.sleep(3600)
        else:
            LOGGER.info('Work is ' + work_type + ' job')

            if work_type == 'doc':
                return_doc(work_json)
            else:
                return_docs(work_json)

        CLIENT_HEALTH_MANAGER.make_call()

    else:
        LOGGER.error('Job type unexpected')
        CLIENT_HEALTH_MANAGER.make_fail_call()


def get_json_info(json_result):
    """
    Return job information from server json
    :param json_result: the json returned from
    """

    job_id = json_result['job_id']
    data = json_result['data']
    return job_id, data


def return_docs(json_result):
    """
    Handles the documents processing necessary for a job
    Calls the /return_docs endpoint of the server to return data for the job it completed
    :param json_result: the json received from the /get_work endpoint
    :return: result from calling /return_docs
    """

    job_id, data = get_json_info(json_result)
    json_info = docs.documents_processor(API_MANAGER, data, job_id, CLIENT_ID)
    path = tempfile.TemporaryDirectory()
    shutil.make_archive('result', 'zip', path.name)
    file_obj = open('result.zip', 'rb')
    r = SERVER_MANAGER.make_docs_return_call(file_obj, json_info)
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
    path = doc.document_processor(API_MANAGER, doc_ids)
    shutil.make_archive('result', 'zip', path.name)
    file_obj = open('result.zip', 'rb')
    json_info = {'job_id': job_id, 'type': 'doc', 'user': CLIENT_ID, 'version': VERSION}
    r = SERVER_MANAGER.make_doc_return_call(file_obj, json_info)
    r.raise_for_status()
    return r


def copy_file_safely(directory, file_path):
    """
    Safely copies a file to a directory; if the file isn't there to be copied, it won't be copied.
    :param directory: Directory to copy to
    :param file_path: File to copy
    """

    if Path(file_path).exists():
        if Path(directory).exists():
            shutil.copy(file_path, directory)
        else:
            LOGGER.warning('File not copied, directory does not exist')
    else:
        LOGGER.warning('File not copied, file does not exist')


def run():
    """
    Working loop
    Get work - Determine type of work - Do work - Return work
    If there is no work in the server, sleep for an hour
    """

    while True:

        try:
            work = SERVER_MANAGER.make_work_call()
        except API_MANAGER.CallFailException:
            LOGGER.debug('API Call Failed...')
            LOGGER.info('Waiting an hour until retry...')
            time.sleep(3600)
            continue

        CLIENT_HEALTH_MANAGER.make_call()
        work_json = json.loads(work.content.decode('utf-8'))

        do_work(work_json)
