import logging
import os.path
import mirrulations_core.documents_core as dc

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='doc_filter.log', format=FORMAT)
d = { 'clientip': '192.168.0.1', 'user': 'FILTERS'}
logger = logging.getLogger('tcpserver')


def search_for_document_in_directory(document_id, directory_path):
    """
    Looks in a directory structure to see if a given document id exists
    :param document_id: the document id being searched
    :param directory_path: The directory path being searched in
    :return: Return the full path if the document exists, else return an empty string
    """
    orgs, dock_id, doc_id = dc.get_doc_attributes(document_id)

    full_path = directory_path + orgs + "/" + dock_id + "/" + doc_id
    doc_json = "doc." + doc_id + ".json"

    if os.path.isfile(full_path + "/" + doc_json):
        return full_path
    else:
        return ""
