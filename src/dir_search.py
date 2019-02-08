import logging
import os.path
import re
import doc_filter as df

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='doc_filter.log', format=FORMAT)
d = { 'clientip': '192.168.0.1', 'user': 'FILTERS'}
logger = logging.getLogger('tcpserver')


PATH = os.getenv("HOME")+"/regulations_data/"


def get_document_id_attributes(document_id):

    if "-" not in document_id:
        return "","",""

    elif "_" in document_id:

        split_name = re.split("[-_]", document_id)
        org = split_name[0] + "_" + split_name[1]
        docket_id = org + "_" + split_name[2]
        document_id = docket_id + "-" + split_name[3]
        return org, docket_id, document_id

    else:
        split_name = re.split("[-]", document_id)
        length = len(split_name)
        count = 0
        for x in range(length):
            if split_name[x].isdigit():
                break
            else:
                count += 1

        org_list = split_name[:count]
        org_list.sort()

        org = df.add_hyphens(org_list)

        docket_id = df.add_hyphens(split_name[:len(split_name) - 1])

        document_id = df.add_hyphens(split_name[:len(split_name)])

        return org,docket_id,document_id


def search_for_document(document_id):
    orgs,dock_id,doc_id = get_document_id_attributes(document_id)

    full_path = PATH + orgs + "/" + dock_id + "/" + doc_id

    if os.path.isfile(full_path + "/doc."+doc_id+".json"):
        return full_path
    else:
        return ""


def search_for_document_temp(document_id, dir):
    orgs,dock_id,doc_id = get_document_id_attributes(document_id)

    full_path = dir + orgs + "/" + dock_id + "/" + doc_id

    print("This is the full temp path:" + full_path)

    if os.path.isfile(full_path + "/doc."+doc_id+".json"):
        return full_path
    else:
        return ""
