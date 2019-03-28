import mirrulations.document_processor as doc
import mirrulations.documents_processor as docs
import mirrulations.api_call_management as man
import requests
import json
import time
import logging
import shutil
import tempfile
import os
from pathlib import Path
from mirrulations.mirrulations_logging import logger
import mirrulations_core.config as config

# These variables are specific to the current implementation
version = "v1.3"

ip = config.read_value('ip')
port = config.read_value('port')

serverurl = "http://" + ip + ":" + port

key = config.read_value('key')
client_id = config.read_value('client_id')

client_health_url = "https://hc-ping.com/457a1034-83d4-4a62-8b69-c71060db3a08"

PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                    '../../')


def get_work(client_id):
    """
    Calls the /get_work endpoint of the server to fetch work to process
    :param client_id: the id of the client calling /get_work
    :return: the result of making a call to get work
    """
    url = serverurl+"/get_work?client_id="+str(client_id)
    result = man.api_call_manager(url)
    logger.critical('Obtained work from server.')
    return result


def get_json_info(json_result):
    """
    Return job information from server json
    :param json_result: the json returned from
    :return:
    """

    job_id = json_result["job_id"]
    urls = json_result["data"]
    return job_id, urls


def return_docs(json_result, client_id):
    """
    Handles the documents processing necessary for a job
    Calls the /return_docs endpoint of the server to return data for the job it completed
    :param json_result: the json received from the /get_work endpoint
    :param client_id: the id of the client that is processing the documents job
    :return: result from calling /return_docs
    """

    job_id, urls = get_json_info(json_result)
    json_info = docs.documents_processor(urls, job_id, client_id)
    path = tempfile.TemporaryDirectory()
    add_client_log_files(path.name, ".")
    shutil.make_archive("result", "zip", path.name)
    fileobj = open('result.zip', 'rb')
    r = requests.post(serverurl + "/return_docs", files={'file': fileobj}, data={'json': json.dumps(json_info)})
    r.raise_for_status()
    logger.info('Returned Docs')
    # local_backup = open('../../mirrulations_local_backup.log', 'a+')
    # mirrulations_log = open('../../mirrulations.log', 'r')
    # local_backup.write(mirrulations_log.read())
    # local_backup.close()
    # mirrulations_log.close()
    try:
        remove_file(PATH + 'mirrulations.log')
    except:
        logger.warning('Failed to delete mirrulations.log')
    return r


def remove_file(filename):
    os.remove(filename)


def return_doc(json_result, client_id):
    """
    Handles the document processing necessary for a job
    Calls the /return_doc endpoint of the server to return data for the job it completed
    :param json_result: the json received from the /get_work endpoint
    :param client_id: the id of the client that is processing the documents job
    :return: result from calling /return_doc
    """

    job_id, doc_dicts = get_json_info(json_result)
    doc_ids = []
    for dic in doc_dicts:
        doc_ids.append(dic['id'])
    path = doc.document_processor(doc_ids)
    add_client_log_files(path.name, ".")
    shutil.make_archive("result", "zip", path.name)
    fileobj = open('result.zip', 'rb')
    r = requests.post(serverurl+"/return_doc",
                      files={'file': ('result.zip', fileobj)},
                      data={'json': json.dumps({"job_id": job_id, "type": "doc",
                                               "user": client_id, "version": version})})
    r.raise_for_status()
    logger.info('Returned Doc')
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
        else:
            logger.warning('File not copied, directory does not exist')
    else:
        logger.warning('File not copied, file does not exist')


def add_client_log_files(directory, log_directory):
    """
    Used to copy client log files into the temp directory to be sent to the server.
    :param directory: Directory to write files to
    :param log_directory: Directory to get files from
    :return:
    """

    copy_file_safely(directory, log_directory + "/mirrulations.log")


def do_work():
    """
    Working loop
    Get work - Determine type of work - Do work - Return work
    If there is no work in the server, sleep for an hour
    :return:
    """

    while True:
        try:
            work = get_work(client_id)
            requests.get(client_health_url)
            work_json = json.loads(work.content.decode('utf-8'))
        except man.CallFailException:
            time.sleep(3600)
        if work_json["type"] == "doc":
            r = return_doc(work_json, client_id)
            requests.get(client_health_url)
        elif work_json["type"] == "docs":
            r = return_docs(work_json, client_id)
            requests.get(client_health_url)
        elif work_json["type"] == "none":
            time.sleep(3600)
            requests.get(client_health_url)
        else:
            logger.error('Job type unexpected')
            requests.get(client_health_url + "/fail")


if __name__ == '__main__':
    do_work()
