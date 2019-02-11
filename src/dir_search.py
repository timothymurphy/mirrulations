import logging
import os.path
import doc_filter as df

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='doc_filter.log', format=FORMAT)
d = { 'clientip': '192.168.0.1', 'user': 'FILTERS'}
logger = logging.getLogger('tcpserver')


PATH = os.getenv("HOME")+"/regulations_data/"


def search_for_document(document_id):
    orgs, dock_id, doc_id = df.get_doc_attributes(document_id)

    full_path = PATH + orgs + "/" + dock_id + "/" + doc_id

    if os.path.isfile(full_path + "/doc."+doc_id+".json"):
        return full_path
    else:
        return ""


def search_for_document_temp(document_id, dir):
    orgs, dock_id, doc_id = df.get_doc_attributes(document_id)

    full_path = dir + orgs + "/" + dock_id + "/" + doc_id

    print("This is the full temp path:" + full_path)

    if os.path.isfile(full_path + "/doc."+doc_id+".json"):
        return full_path
    else:
        return ""
