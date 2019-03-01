import re
import logging

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='doc_filter.log', format=FORMAT)
d = { 'clientip': '192.168.0.1', 'user': 'FILTERS'}
logger = logging.getLogger('tcpserver')


def get_doc_attributes(document_id):
    """
    Get the organization(s), the docket_id and the document_id from a file name
    :param file_name: name of the file to extract attributes of the document name
    :return: orgs: The organizations(s),
             docket_id: the docket_id,
             document_id: the document_id
    """

    logger.debug('Function Successful: % s',
                   'get_doc_attributes: get_doc_attributes successfully called from process_doc', extra=d)

    if "_" in document_id:
        logger.debug('Calling Function: % s',
                       'get_doc_attributes: get_doc_attributes calling split', extra=d)
        split_name = re.split("[-_]", document_id)
        logger.debug('Function Successful: % s',
                       'get_doc_attributes: get_doc_attributes successfully called split', extra=d)

        org = split_name[0] + "_" + split_name[1]
        docket_id = org + "_" + split_name[2]
        document_id = docket_id + "-" + split_name[3]
        logger.debug('Returning: %s',
                       'get_doc_attributes: returning the organization, docket_id, and document_id', extra=d)
        return org, docket_id, document_id

    else:
        logger.debug('Calling Function: % s',
                       'get_doc_attributes: get_doc_attributes calling split', extra=d)
        split_name = re.split("[-]", document_id)
        logger.debug('Function Successful: % s',
                       'get_doc_attributes: get_doc_attributes successfully called split', extra=d)
        length = len(split_name)
        count = 0
        for x in range(length):
            if split_name[x].isdigit():
                break
            else:
                count += 1

        org_list = split_name[:count]
        org_list.sort()

        logger.debug('Calling Function: % s',
                       'get_doc_attributes: get_doc_attributes calling add_hyphens', extra=d)
        org = add_hyphens(org_list)
        logger.debug('Function Successful: % s',
                       'get_doc_attributes: get_doc_attributes successfully called add_hyphens', extra=d)

        logger.debug('Calling Function: % s',
                       'get_doc_attributes: get_doc_attributes calling add_hyphens', extra=d)
        docket_id = add_hyphens(split_name[:len(split_name) - 1])
        logger.debug('Function Successful: % s',
                       'get_doc_attributes: get_doc_attributes successfully called add_hyphens', extra=d)

        logger.debug('Calling Function: % s',
                       'get_doc_attributes: get_doc_attributes calling add_hyphens', extra=d)
        document_id = add_hyphens(split_name[:len(split_name)])
        logger.debug('Function Successful: % s',
                       'get_doc_attributes: get_doc_attributes successfully called add_hyphens', extra=d)

        logger.debug('Returning: %s',
                       'get_doc_attributes: returning the organization, docket_id, and document_id', extra=d)
        return org,docket_id,document_id


def add_hyphens(list):
    """
    Adds hyphens between the list of strings passed
    :param list: the list to be hyphenated
    :return: A string of the list with hyphens in-between
    """
    logger.debug('Function Successful: % s',
                   'add_hyphens: add_hyphens successfully called from get_doc_attributes', extra=d)
    logger.info('Hyphenating strings...')

    hyphened_string = ""
    for x in range(len(list)):

        if x == 0:
            if len(list) == 1:
                hyphened_string = list[x]
            else:
                hyphened_string = list[x] + "-"

        elif x == len(list) - 1:
            hyphened_string = hyphened_string + list[x]

        else:
            hyphened_string = hyphened_string + list[x] + "-"

    logger.debug('Returning: %s',
                   'add_hyphens: returning the hyphened_string', extra=d)
    logger.info('Strings hyphenated')

    return hyphened_string
