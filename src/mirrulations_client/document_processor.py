import tempfile
from mirrulations_client.documents_processor import *
import mirrulations_core.config as config
from mirrulations.mirrulations_logging import logger

client_id = config.read_value('CLIENT', 'CLIENT_ID')


def document_processor(api_manager, doc_ids):
    dirpath = tempfile.TemporaryDirectory()
    for doc_id in doc_ids:
        try:
            result = api_manager.make_document_call(doc_id)
            total = get_extra_documents(api_manager, result, dirpath.name, doc_id)
        except api_manager.CallFailException:
            logger.error('Doc ID error')
    return dirpath


def save_document(dirpath, doc_json, documentId):
    """
    Saves the json of the document call
    :param dirpath: path to the directory where the json will be saved
    :param doc_json: the json received from the api call
    :param documentId: the string of a documentId
    :return:
    """
    location = dirpath + "/doc." + documentId + ".json"
    with open(location , "w+") as f:
        json.dump(doc_json, f)


def download_document(dirpath, documentId, result, type):
    """
    Saves the other file formats of the document call
    :param dirpath: path to the directory where the download will be saved
    :param documentId: the string of a documentId
    :param result: the result received from the api call
    :param type: the type of file that will be saved
    :return:
    """
    # These are special cases where the api representation is different from the user's interpretation
    if(type == "excel12book"):
        type = "xlsx"
    if(type == "msw12"):
        type = "doc"
    with open(dirpath + "/doc." + documentId + "." + type, 'wb') as f:
        for chunk in result.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


def get_extra_documents(api_manager, result, dirpath, documentId):
    """
    Download the json of the result from the original api call
    Determine if the document has additional file formats that need to be downloaded
    Determines if the document has attachments that need to be downloaded
    :param result: the result of the api call
    :param dirpath: path to the directory where the download will be saved
    :param documentId: the string of a documentId
    :return: the total number of requests required to download all of them
    """
    doc_json = json.loads(result.text)
    save_document(dirpath, doc_json, documentId)
    total_requests = 0
    total_requests += download_doc_formats(api_manager, dirpath, doc_json, documentId)
    total_requests += download_attachments(api_manager, dirpath, doc_json, documentId)

    return total_requests


def download_doc_formats(api_manager, dirpath, doc_json, documentId):
    """
    Download the other formats for the document
    :param dirpath: path to the directory where the download will be saved
    :param doc_json: the json from a single document api call
    :param documentId: the string of a documentId
    :return: the total number of requests used to download the extra formats
    """
    total_requests = 0
    try:
        extra_formats = doc_json["fileFormats"]
        total_requests += len(extra_formats)
        for extra_doc in extra_formats:
            result = api_manager.make_call(extra_doc)
            here = extra_doc.index("contentType") + 12
            type = extra_doc[here:]
            download_document(dirpath, documentId, result, type)
    except KeyError:
        pass
    except api_manager.CallFailException:
        logger.error('Error - Call failed')
        pass
    return total_requests


def download_attachments(api_manager, dirpath, doc_json, documentId):
    """
    Download the other attachments for the document
    :param dirpath: path to the directory where the download will be saved
    :param doc_json: the json from a single document api call
    :param documentId: the string of a documentId
    :return: the total number of requests used to download the extra attachments
    """
    total_requests = 0
    try:
        extra_attachments = doc_json["attachments"]
        total_requests += len(extra_attachments)
        for attachment in extra_attachments:
            attachment_formats = attachment["fileFormats"]
            for a_format in attachment_formats:
                here = str(a_format).index("contentType") + 12
                type = str(a_format)[here:]
                result = api_manager.make_document_call(a_format)
                download_document(dirpath, documentId, result, type)
    except KeyError:
        pass
    except api_manager.CallFailException:
        logger.error('Error - Call failed')
        pass
    return total_requests
