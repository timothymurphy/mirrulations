import logging
import os.path
import mirrulations.doc_filter as df

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='doc_filter.log', format=FORMAT)
d = { 'clientip': '192.168.0.1', 'user': 'FILTERS'}
logger = logging.getLogger('tcpserver')


PATH = os.getenv("HOME")+"/regulations_data/"


def search_for_document(document_id):
    """
    Called by the server to check to see if a document exists in the directory structure
    :param document_id:
    :return: Return the full path if the document exists, else return an empty string
    """
    orgs, dock_id, doc_id = df.get_doc_attributes(document_id)

    full_path = PATH + orgs + "/" + dock_id + "/" + doc_id
    doc_json = "doc." + doc_id + ".json"

    if os.path.isfile(full_path + "/" + doc_json):
        return full_path
    else:
        return ""


def search_for_document_test_directory(document_id, dir):
    """
    Same as the search_for_document.
    This is only to be used for testing purposes.
    :param document_id:
    :param dir: The test directory being used
    :return: Return the full path if the document exists, else return an empty string
    """
    orgs, dock_id, doc_id = df.get_doc_attributes(document_id)

    full_path = dir + orgs + "/" + dock_id + "/" + doc_id
    doc_json = "doc." + doc_id + ".json"

    if os.path.isfile(full_path + "/" + doc_json):
        return full_path
    else:
        return ""
