import document_processor as doc
import documents_processor as docs
import api_call_management as man
import requests
import json
import zipfile
import os
import time

serverurl = "http://127.0.0.1:5000"
version = "v1.0"
home = os.getenv("HOME")
with open(home + '/.env/regulationskey.txt') as f:
    key = f.readline().strip()
    client_id = f.readline().strip()


def get_work(client_id):
    """
    Calls the /get_work endpoint of the server to fetch work to process
    :param client_id: the id of the client calling /get_work
    :return: the result of making a call to get work
    """
    url = serverurl+"/get_work?client_id="+str(client_id)
    return man.api_call_manager(url)


def return_docs(json_result, client_id):
    """
    Handles the documents processing necessary for a job
    Calls the /return_docs endpoint of the server to return data for the job it completed
    :param json_result: the json received from the /get_work endpoint
    :param client_id: the id of the client that is processing the documents job
    :return: result from calling /return_docs
    """
    job_id = json_result["job_id"]
    urls = json_result["data"]
    json = docs.documents_processor(urls,job_id,client_id)
    r = requests.post(serverurl+"/return_docs", data=dict(json=json))
    r.raise_for_status()
    return r


def return_doc(json_result, client_id):
    """
    Handles the document processing necessary for a job
    Calls the /return_doc endpoint of the server to return data for the job it completed
    :param json_result: the json received from the /get_work endpoint
    :param client_id: the id of the client that is processing the documents job
    :return: result from calling /return_doc
    """
    job_id = json_result["job_id"]
    doc_dicts = json_result["data"]
    doc_ids = []
    for d in doc_dicts:
        doc_ids.append(d['id'])

    result = zipfile.ZipFile("result.zip", 'w', zipfile.ZIP_DEFLATED)
    path = doc.document_processor(doc_ids)
    for root, dirs, files in os.walk(path.name):
        for file in files:
            result.write(os.path.join(root, file))
    path.cleanup()
    r = requests.post(serverurl+"/return_doc", files={'file':result.extractall()},
                      data={'json':json.dumps({"job_id" : job_id, "type" : "doc", "client_id": client_id, "version" : version })})
    r.raise_for_status()
    return r


def do_work():
    """
    Working loop
    Get work - Determine type of work - Do work - Return work
    If there is no work in the server, sleep for an hour
    :return:
    """
    while True:
        work = get_work(client_id)
        work_json = work.content.decode('utf-8')
        if work_json["type"] == "doc":
            r = return_doc(work_json, client_id)
        elif work_json["type"] == "docs":
            r = return_docs(work_json, client_id)
        elif work_json["type"] == "none":
            time.sleep(3600)
        else:
            raise AttributeError
